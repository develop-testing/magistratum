import redis

client = redis.Redis(
    host="fast-store", port=6379, decode_responses=True, password="fhy6asd"
)
