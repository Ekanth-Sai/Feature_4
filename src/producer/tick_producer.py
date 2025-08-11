import time
import json
import random 
from datetime import datetime, timezone
from kafka import KafkaProducer

KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "market.ticks"
SYMBOLS = ["RELIANCE", "TCS", "INFY"]

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP,
    value_serializer = lambda v: json.dumps(v).encode("utf-8"),
)

def current_ts():
    return datetime.now(timezone.utc).isoformat()

def run():
    price_map = {"RELIANCE": 2550.0, "TCS": 3500.0, "INFY": 1500.0}

    while True:
        for s in SYMBOLS:
            price_map[s] = price_map[s] + random.uniform(-1.0, 1.0)
            tick = {
                "ts": current_ts(),
                "symbol": s,
                "price": round(price_map[s], 2),
                "size": random.choice([10, 20, 50, 100]),
            }
            producer.send(TOPIC, tick)
        producer.flush()
        time.sleep(0.5)
if __name__ == "__main__":
    print("Starting tick generator")
    run()