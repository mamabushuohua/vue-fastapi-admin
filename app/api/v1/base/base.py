import jwt
from fastapi import APIRouter, Header

from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.models.admin import Api, Menu, Role, User
from app.schemas.base import Fail, Success
from app.schemas.login import CredentialsSchema, JWTOut
from app.schemas.users import UpdatePassword
from app.settings import settings
from app.utils.jwt_utils import create_tokens
from app.utils.password import get_password_hash, verify_password
from app.utils.token_utils import (
    store_token_in_redis,
    validate_refresh_token_from_redis,
    revoke_all_user_tokens_in_redis,
)

router = APIRouter()


@router.post("/access_token", summary="获取token")
async def login_access_token(credentials: CredentialsSchema):
    user: User = await user_controller.authenticate(credentials)
    await user_controller.update_last_login(user.id)

    # Create both access and refresh tokens
    access_token, refresh_token = create_tokens(user_id=user.id, username=user.username, is_superuser=user.is_superuser)

    # Store tokens in Redis
    await store_token_in_redis(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        is_superuser=user.is_superuser,
    )

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
        # Validate refresh token from Redis
        token_data = await validate_refresh_token_from_redis(refresh_token)
        if not token_data:
            return Fail(code=401, msg="无效的刷新令牌")

        user_id = token_data["user_id"]
        username = token_data["username"]
        is_superuser = token_data["is_superuser"]

        # Get user from database
        user = await User.filter(id=user_id).first()
        if not user:
            return Fail(code=401, msg="用户不存在")

        # Create new access and refresh tokens
        new_access_token, new_refresh_token = create_tokens(
            user_id=user.id, username=username, is_superuser=is_superuser
        )

        # Store new tokens in Redis
        await store_token_in_redis(
            user_id=user.id,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            username=username,
            is_superuser=is_superuser,
        )

        data = JWTOut(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            username=username,
        )
        return Success(data=data.model_dump())
    except jwt.ExpiredSignatureError:
        return Fail(code=401, msg="刷新令牌已过期")
    except jwt.DecodeError:
        return Fail(code=401, msg="无效的刷新令牌")
    except Exception as e:
        return Fail(code=500, msg=f"刷新令牌处理失败: {str(e)}")


@router.post("/logout", summary="登出", dependencies=[DependAuth])
async def logout(token: str = Header(..., description="access token")):
    try:
        # Get user ID from token
        try:
            decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
            user_id = decode_data.get("user_id")
        except jwt.DecodeError:
            return Fail(code=401, msg="无效的访问令牌")
        except jwt.ExpiredSignatureError:
            return Fail(code=401, msg="访问令牌已过期")

        # Revoke all user tokens in Redis
        await revoke_all_user_tokens_in_redis(user_id)

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

    # Revoke all user tokens when password is changed for security
    await revoke_all_user_tokens_in_redis(user_id)

    return Success(msg="修改成功")
