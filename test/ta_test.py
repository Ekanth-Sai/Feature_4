import pandas as pd
from src.utils import ta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

prices = pd.Series([10, 12, 14, 16, 15, 17, 18, 19])

print("SMA with window 3: ")
print(ta.sma(prices, 3))

print("\nEMA with window 3: ")
print(ta.ema(prices, 3))

print("\nRSI with window 14: ")
print(ta.rsi(prices, 14))