from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.models.admin import Api, Menu, Role, User, RefreshToken
from app.schemas.base import Fail, Success
from app.schemas.login import CredentialsSchema, JWTOut
from app.schemas.users import UpdatePassword
from app.settings import settings
from app.utils.jwt_utils import create_tokens
from app.utils.password import get_password_hash, verify_password

router = APIRouter()


@router.post("/access_token", summary="获取token")
async def login_access_token(credentials: CredentialsSchema):
    user: User = await user_controller.authenticate(credentials)
    await user_controller.update_last_login(user.id)

    # Create both access and refresh tokens
    access_token, refresh_token = create_tokens(user_id=user.id, username=user.username, is_superuser=user.is_superuser)

    # Store refresh token in database
    # Use the same expiration time as in the JWT token
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    await RefreshToken.create(token=refresh_token, user=user, expires_at=expires_at)

    data = JWTOut(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
    )
    return Success(data=data.model_dump())


@router.get("/userinfo", summary="查看用户信息", dependencies=[DependAuth])
async def get_userinfo():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    data = await user_obj.to_dict(exclude_fields=["password"])
    data["avatar"] = "https://avatars.githubusercontent.com/u/54677442?v=4"
    return Success(data=data)


@router.get("/usermenu", summary="查看用户菜单", dependencies=[DependAuth])
async def get_user_menu():
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = await Menu.all()
    else:
        role_objs: list[Role] = await user_obj.roles
        for role_obj in role_objs:
            menu = await role_obj.menus
            menus.extend(menu)
        menus = list(set(menus))
    parent_menus: list[Menu] = []
    for menu in menus:
        if menu.parent_id == 0:
            parent_menus.append(menu)
    res = []
    for parent_menu in parent_menus:
        parent_menu_dict = await parent_menu.to_dict()
        parent_menu_dict["children"] = []
        for menu in menus:
            if menu.parent_id == parent_menu.id:
                parent_menu_dict["children"].append(await menu.to_dict())
        res.append(parent_menu_dict)
    return Success(data=res)


@router.get("/userapi", summary="查看用户API", dependencies=[DependAuth])
async def get_user_api():
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    if user_obj.is_superuser:
        api_objs: list[Api] = await Api.all()
        apis = [api.method.lower() + api.path for api in api_objs]
        return Success(data=apis)
    role_objs: list[Role] = await user_obj.roles
    apis = []
    for role_obj in role_objs:
        api_objs: list[Api] = await role_obj.apis
        apis.extend([api.method.lower() + api.path for api in api_objs])
    apis = list(set(apis))
    return Success(data=apis)


@router.post("/refresh_token", summary="刷新token")
async def refresh_access_token(refresh_token: str):
    try:

        # Get the refresh token object from database
        refresh_token_obj = await RefreshToken.filter(token=refresh_token, is_revoked=False).first()
        if not refresh_token_obj:
            return Fail(code=401, msg="无效的刷新令牌")

        # Use the existing is_refresh_token_valid function to validate the refresh token
        from app.core.dependency import AuthControl

        user = await AuthControl.is_refresh_token_valid(refresh_token)

        if not user:
            return Fail(code=401, msg="非法的用户刷新令牌")
        # # Mark current refresh token as revoked
        # refresh_token_obj.is_revoked = True
        # await refresh_token_obj.save()

        # Create new access and refresh tokens
        new_access_token, new_refresh_token = create_tokens(
            user_id=user.id, username=user.username, is_superuser=user.is_superuser
        )

        # Store new refresh token in database
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        await RefreshToken.create(token=new_refresh_token, user=user, expires_at=expires_at)

        data = JWTOut(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            username=user.username,
        )
        return Success(data=data.model_dump())
    except Exception as e:
        refresh_token_obj.is_revoked = True
        await refresh_token_obj.save()
        # Handle specific JWT exceptions
        return Fail(code=401, msg=f"{repr(e)}")


@router.post("/logout", summary="登出", dependencies=[DependAuth])
async def logout(refresh_token: str):
    try:
        # Mark refresh token as revoked
        refresh_token_obj = await RefreshToken.filter(token=refresh_token).first()
        if refresh_token_obj:
            refresh_token_obj.is_revoked = True
            await refresh_token_obj.save()

        return Success(msg="登出成功")
    except Exception as e:
        return Fail(code=500, msg=f"登出失败: {str(e)}")


@router.post("/update_password", summary="修改密码", dependencies=[DependAuth])
async def update_user_password(req_in: UpdatePassword):
    user_id = CTX_USER_ID.get()
    user = await user_controller.get(user_id)
    verified = verify_password(req_in.old_password, user.password)
    if not verified:
        return Fail(msg="旧密码验证错误！")
    user.password = get_password_hash(req_in.new_password)
    await user.save()
    return Success(msg="修改成功")
