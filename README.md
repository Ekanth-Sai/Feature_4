# File analysis

## src/utils/ta.py

### Code details

- It is the Technical Analyser herlper module.
- It contains 3 functions:
  - `sma()` which calculates the `Simple Moving Average` of a stock price series
  - `ema()` which calculates the `Exponential Moving Average` which gives more weightage to recent prices.
  - `rsi()` which calculates the `Relative Strength Index`, an indicator that tells whether a stock has been overbrought or oversold.

### Math and logic

```python
def sma(series: pd.Series, window: int):
    return series.rolling(window).mean()
```

- `series` is the price data from the stock chart
- `window` is the average we calculate after a certain period (I have taken days).
- `.rolling(window)` makes a sliding window across the values
- `.mean()` takes the average

```python
def ema(series: pd.Series, window: int):
    return series.ewm(span=window, adjust=False).mean()
```

- `ewm()` is the Exponentiall Weighted Moving average
- EMA gives more weightage to recent price changes. Makes it react faster recent changes.
- `span = window` controls how quickly the weight decays (how quickly older data loses its influence while calculating)
- `.mean()` takes the average and applies the exponential weighting
  
```python
def rsi(series: pd.Series, window: int = 14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=window, min_periods=1).mean()
    ma_down = down.rolling(window=window, min_periods=1).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))
```

- `delta = series.diff()` finds the daily price change
- `up` keeps only the posituve changes, while the `down` keeps only the negative changes (we multiply with -1 to store it as a positive number)
- `ma_up` gives the average gain over the last `window` days
- `ma_down` gives the average loss over the last `window` days
- `RS` which is the relative strength gives the average of gains and losses.
- `RSI = 100 - (100 / (1 + rs))` is the RSI formula which governs whether a stock has been overbrought or oversold. The result will always lie between 0 and 100. If RSI > 70, it is overbrought, meaning it might go down. If RSI < 30, it is oversold, meaning it will go up. I added `1e-9` so that, if `ma_down` is 0, it will avoid division by 0.

## src/features/redis.py

- This file is a Redis client utility. Redis is a super fast in-memory database that can store and retrieve small bits of data in ms

### Code Details

- It stores features and retrieves them when needed.
- For example, suppose we calculate RSI, SMA, EMA from `ta.py` for "AAPL" (Apple) ticker in python, we store them in redis, which later can be pulled by another service without recomputing.

```python
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses = True)
```

- `decode_responses = True` converts Redis responses, which are usually in bytes, to python strings.

## src/producer/tick_producer.py

- A fake stock market price feed that publishes data into Kafka.
- It pretends to be a real-time market data source. As I am only testing it, I didn't connect it to any official resources such as NSE/BSE.
- I am simulating here:
  - Live price changes (using `random walk` algo)
  - I am sending data to Kafka so that the other integrated services can read it. This process is called as Producer in Kafka terminilogy.

### Code Details

```python
KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "market.ticks"
SYMBOLS = ["RELIANCE", "TCS", "INFY"]
```

- `localhost:9092` is the address of the Kafka server on localhost
- `TOPIC` is like an email address.
- `SYMBOLS` is the companies whose stocks we are simulating.

```python
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
```

- `KafkaProducer` connects us to Kafka and lets us send data
- `value_serializer()` converts data into JSON format, then into bytes, as Kafka accepts only bytes.

```python
def current_ts():
    return datetime.now(timezone.utc).isoformat()
```

- Returns current time in utc, which acts as a timestamp for each tick.

```python
price_map = {"RELIANCE": 2550.0, "TCS": 3500.0, "INFY": 1500.0}
```

- Initial prices for each stock.

```python
price_map[s] += random.uniform(-1.0, 1.0)
```

- This is the random walk algorithm. It simulates price change by adding a number in the range of -1 and 1.

```python
tick = {
    "ts": current_ts(),
    "symbol": s,
    "price": round(price_map[s], 2),
    "size": random.choice([10, 20, 50, 100]),
}
```

- `ts` is the timestamp
- `symbol` is the stock ticker name
- `price` is the latest stock price rounded off to 2 places.
- `size` is the number of shares traded which is picked randomly.

```python
producer.send(TOPIC, tick)
producer.flush()
```

- `send()` sends the message to Kafka
- `flush()` forces all buffered messages to be sent immediately.

```python
time.sleep(0.5)
```

- Waits for half a second so that each symbol gets 2 price updates per second.

### How to run / execute

- Go to the Kafka folder. From inside the terminal, run the given code. Keep the terminal open as Zookeeper must be running.

```bash
./bin/zookeeper-server-start.sh config/zookeeper.properties
```

- Open a new terminal in the same directory, and keep this running:

```bash
./bin/kafka-server-start.sh config/server.properties
```

- Open a new terminal. If you are running this for the first time, execute this bash

```bash
./bin/kafka-topics.sh --create --topic market.ticks --bootstrap-server localhost:9092
```

- Go to the project folder, and run this:

```bash
python src/producer/tick_producer.py
```

- By running this, we will see:
  - `Starting tick producer`

- Open another terminal in the Kafka folder, and run the command. The output will be generated

```bash
./bin/kafka-console-consumer.sh --topic market.ticks --from-beginning --bootstrap-server localhost:9092
```

## src/news/news_producer.py

- This file is a python script that simulates financial news headlines and sends them to Kafka so that the consumers can process them in real time. It is like a fake news feed that runs continously and publishes a `JSON` stream to Kafka.

### Code Details

```python
SAMPLE_HEADLINES = [
    ("positive", "announces higher quarterly profit than expected"),
    ("negative", "faces regulatory inquiry into operations"),
    ("neutral", "board meeting scheduled next week"),
]
```

- It is a list of `(tone, text)` pairs, where `tone = sentiment` and `text = headlines snippet`. Since this is a PoC, I used basic text. Will upgrade for real time.

```python
def run():
    while True:
        sym = random.choice(SYMBOLS)
        tone, txt = random.choice(SAMPLE_HEADLINES)
        msg = {
            "id": f"news_{int(time.time()*1000)}",
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
```

- I kept an infinite loop as the news should be generated an analyzed continously.
- We pick a random text and its respective tone.
- `"id"` is the unique id which is generated as the ms after each epoch generation.
- `"source"`: `"sim"` means that the source is simulated.
- `.send()` queues it for sending. `.flush()` forces to be sent.

### How to run / execute

- Change directory to the Kafka folder. Start the zookeeper.

```bash
./bin/zookeeper-server-start.sh config/zookeeper.properties
```

- Open another terminal with the directory of Kafka folder.

```bash
./bin/kafka-server-start.sh config/server.properties
```

- Open another terminal to create a topic. Only need to be executed the first time.

```bash
./bin/kafka-topics.sh --create --topic news.stream --bootstrap-server localhost:9092
```

- Go to the root directory and execute the file.

```bash
python src/news/news_producer.py
```

- In a new terminal

```bash
./bin/kafka-console-consumer.sh --topic news.stream --from-beginning --bootstrap-server localhost:9092
```
