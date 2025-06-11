import redis.asyncio as redis

from app.models.settings import Settings

config = Settings()
redis_client = redis.from_url(config.redis_url, decode_responses=True)


def get_cache() -> redis.Redis:
    return redis_client
