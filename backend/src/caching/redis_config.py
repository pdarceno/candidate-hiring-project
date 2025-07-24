import os
from redis import Redis

def get_redis_cache_connection():
    redis_port = os.getenv('REDIS_PORT')
    redis_host = os.getenv('REDIS_HOST')
    return Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
