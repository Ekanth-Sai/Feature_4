import redis
import json
import os 

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, decode_responses = True)

def set_feature(symbol: str, feature_dict: dict):
    key = f"features: {symbol}"
    r.set(key, json.dumps(feature_dict))

def get_feature(symbol: str):
    key = f"features: {symbol}"
    v = r.get(key)

    if v:
        return json.loads(v)
    
    return None