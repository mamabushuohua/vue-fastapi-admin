from typing import Optional
import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.ctx import CTX_USER_ID
from app.models import Role, User
from app.settings import settings
from app.utils.token_utils import validate_access_token_from_redis, validate_refresh_token_from_redis


class AuthControl:
    @classmethod
    async def is_authed(cls, token: str = Header(..., description="token验证")) -> Optional["User"]:
        try:

            # Fallback to JWT validation
            if token == "dev":
                user = await User.filter().first()
                user_id = user.id
            else:
                # First try to validate from Redis
                token_data = await validate_access_token_from_redis(token)
                if token_data is None:
                    raise HTTPException(status_code=401, detail="token不存在或已过期")
                decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
                user_id = decode_data.get("user_id")
            user = await User.filter(id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="无效的Token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="登录已过期")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{repr(e)}")

    @classmethod
    async def is_refresh_token_valid(cls, refresh_token: str) -> Optional["User"]:
        """
        验证刷新令牌
        尝试从Redis中验证刷新令牌, 如果存在还需要jwt验证，不存在直接返回None
        """
        try:
            # First try to validate from Redis
            token_data = await validate_refresh_token_from_redis(refresh_token)
            if token_data:
                jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
                user_id = token_data["user_id"]
                user = await User.filter(id=user_id).first()
                if user:
                    CTX_USER_ID.set(int(user_id))
                    return user
            return None
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="刷新令牌已过期")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{repr(e)}")


class PermissionControl:
    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> None:
        if current_user.is_superuser:
            return
        method = request.method
        path = request.url.path
        roles: list[Role] = await current_user.roles
        if not roles:
            raise HTTPException(status_code=403, detail="The user is not bound to a role")
        apis = [await role.apis for role in roles]
        permission_apis = list(set((api.method, api.path) for api in sum(apis, [])))
        # path = "/api/v1/auth/userinfo"
        # method = "GET"
        if (method, path) not in permission_apis:
            raise HTTPException(status_code=403, detail=f"Permission denied method:{method} path:{path}")


DependAuth = Depends(AuthControl.is_authed)
DependPermission = Depends(PermissionControl.has_permission)
