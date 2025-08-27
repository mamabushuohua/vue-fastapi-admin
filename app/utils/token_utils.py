import json
import time
from typing import Optional

from app.core.redis import get_redis
from app.settings.config import settings


async def store_token_in_redis(user_id: int, access_token: str, refresh_token: str, username: str, is_superuser: bool):
    """将token存储在Redis中"""
    redis_client = await get_redis()

    # 计算过期时间（秒）
    access_token_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_token_expire = settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60

    # 存储access token
    access_token_key = f"access_token:{user_id}:{access_token}"
    access_token_data = {
        "user_id": user_id,
        "username": username,
        "is_superuser": is_superuser,
        "token": access_token,
        "created_at": int(time.time()),
    }
    await redis_client.setex(access_token_key, access_token_expire, json.dumps(access_token_data))

    # 存储refresh token
    refresh_token_key = f"refresh_token:{user_id}:{refresh_token}"
    refresh_token_data = {
        "user_id": user_id,
        "username": username,
        "is_superuser": is_superuser,
        "token": refresh_token,
        "created_at": int(time.time()),
    }
    await redis_client.setex(refresh_token_key, refresh_token_expire, json.dumps(refresh_token_data))

    # 存储用户的所有token，用于登出时全部清除
    user_tokens_key = f"user_tokens:{user_id}"
    await redis_client.sadd(user_tokens_key, access_token_key, refresh_token_key)
    # 设置用户token集合的过期时间与refresh token相同
    await redis_client.expire(user_tokens_key, refresh_token_expire)


async def validate_access_token_from_redis(token: str) -> Optional[dict]:
    """从Redis验证access token"""
    redis_client = await get_redis()

    # 查找所有可能的access token key
    pattern = f"access_token:*:{token}"
    keys = await redis_client.keys(pattern)

    if not keys:
        return None

    # 获取第一个匹配的token数据
    token_data = await redis_client.get(keys[0])
    if not token_data:
        return None

    return json.loads(token_data)


async def validate_refresh_token_from_redis(token: str) -> Optional[dict]:
    """从Redis验证refresh token"""
    redis_client = await get_redis()

    # 查找所有可能的refresh token key
    pattern = f"refresh_token:*:{token}"
    keys = await redis_client.keys(pattern)

    if not keys:
        return None

    # 获取第一个匹配的token数据
    token_data = await redis_client.get(keys[0])
    if not token_data:
        return None

    return json.loads(token_data)


async def revoke_token_in_redis(user_id: int, token: str, token_type: str = "access"):
    """在Redis中撤销token"""
    redis_client = await get_redis()

    # 构造token key
    token_key = f"{token_type}_token:{user_id}:{token}"

    # 从用户token集合中移除
    user_tokens_key = f"user_tokens:{user_id}"
    await redis_client.srem(user_tokens_key, token_key)

    # 删除token
    await redis_client.delete(token_key)


async def revoke_all_user_tokens_in_redis(user_id: int):
    """撤销用户的所有token"""
    redis_client = await get_redis()

    # 获取用户的所有token key
    user_tokens_key = f"user_tokens:{user_id}"
    token_keys = await redis_client.smembers(user_tokens_key)

    if token_keys:
        # 删除所有token
        if token_keys:
            await redis_client.delete(*token_keys)

        # 删除用户token集合
        await redis_client.delete(user_tokens_key)


async def is_token_revoked_in_redis(user_id: int, token: str, token_type: str = "access") -> bool:
    """检查token是否已被撤销"""
    redis_client = await get_redis()

    # 构造token key
    token_key = f"{token_type}_token:{user_id}:{token}"

    # 检查token是否存在
    return not await redis_client.exists(token_key)
