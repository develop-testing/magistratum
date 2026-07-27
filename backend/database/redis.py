import os

import redis

client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "fast-store"),
    port=6379,
    decode_responses=True,
    password=os.environ.get("REDIS_PASSWORD", ""),
)
