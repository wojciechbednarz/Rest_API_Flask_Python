"""
This file contains the blocklist of the JWT tokens. It will be imported by app and the logout resource so that tokens
can be added to the blocklist when the user logs out.
"""

# BLOCKLIST = set()

import redis

redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)


def add_token_to_blocklist(jti):
    redis_client.set(jti, 'true')


def is_token_in_blocklist(jti):
    return redis_client.exists(jti) == 1
