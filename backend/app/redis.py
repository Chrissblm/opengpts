import os
from redis.client import Redis as RedisType
from langchain.utilities.redis import get_client
import sys

CLIENT: RedisType | None = None


def get_redis_client() -> RedisType:
    """Get a Redis client."""
    global CLIENT

    if CLIENT is not None:
        return CLIENT

    url = os.environ.get("REDIS_URL")
    if not url:
        raise ValueError("REDIS_URL not set")
    CLIENT = get_client(url, socket_keepalive=True)
    return CLIENT

#Added this from the opengpt's issues area
def clean(user_id: str) -> bool:
    client = get_redis_client()
    keys_threads = client.keys(f"opengpts:{user_id}:thread:*")
    client.delete(*keys_threads)
    client.delete(f"opengpts:{user_id}:threads")
    return True

# if __name__ == "__main__":
#     user_id = sys.argv[1]
#     if not user_id:
#         raise ValueError("user_id not set")
#     clean(user_id)