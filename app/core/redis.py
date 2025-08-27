import redis.asyncio as redis
from app.settings.config import settings

# Redis连接实例
redis_client: redis.Redis = None


async def init_redis():
    """初始化Redis连接"""
    global redis_client

    # 构建Redis连接URL
    if settings.REDIS_PASSWORD:
        redis_url = (
            f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
    else:
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)


async def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis():
    """获取Redis客户端实例"""
    global redis_client
    if not redis_client:
        await init_redis()
    return redis_client
