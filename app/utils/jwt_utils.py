import jwt
from datetime import datetime, timedelta, timezone

from app.schemas.login import JWTPayload, RefreshTokenPayload
from app.settings.config import settings


def create_access_token(*, data: JWTPayload):
    payload = data.model_dump().copy()
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(*, data: RefreshTokenPayload):
    payload = data.model_dump().copy()
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_tokens(*, user_id: int, username: str, is_superuser: bool):
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expire = datetime.now(timezone.utc) + access_token_expires

    access_token_payload = JWTPayload(
        user_id=user_id, username=username, is_superuser=is_superuser, exp=access_token_expire
    )

    access_token = create_access_token(data=access_token_payload)

    # Create refresh token (7 days expiration)
    refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token_expire = datetime.now(timezone.utc) + refresh_token_expires

    refresh_token_payload = RefreshTokenPayload(
        user_id=user_id, username=username, is_superuser=is_superuser, exp=refresh_token_expire
    )

    refresh_token = create_refresh_token(data=refresh_token_payload)

    return access_token, refresh_token
