import time, random, json
from datetime import datetime, timezone
from kafka import KafkaProducer 

KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "news.stream"
SYMBOLS = ["RELIANCE", "TCS", "INFY"]

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP,
    value_serializer = lambda v: json.dumps(v).encode("utf-8"),
)

SAMPLE_HEADLINES = [
    ("positive", "announces higher quarterly profit than expected"),
    ("negative", "faces regulatory inquiry into operations"),
    ("neutral", "board meetin scheduled next week")
]

def run():
    while True:
        sym = random.choice(SYMBOLS)
        tone, txt = random.choice(SAMPLE_HEADLINES)
        msg = {
            "id": f"news_{int(time.time() * 100)}",
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": "sim",
            "lang": "en",
            "symbol": sym,
            "text": f"{sym} {txt}",
            "tone": tone,
        }
        producer.send(TOPIC, msg)
        producer.flush()
        time.sleep(random.uniform(5, 20))

if __name__ == "__main__":
    print("Starting news producer")
    run()