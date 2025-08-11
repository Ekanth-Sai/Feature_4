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
