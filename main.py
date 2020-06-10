from FileGatherer import FileGatherer
from DataStorage import DataStorage
import pandas as pd

ticker_csv = pd.read_csv("constituents_csv.csv")["Symbol"]
tickers = []
for ticker in ticker_csv:
    tickers.append(ticker)

tickers = tickers[:2]

dicts = FileGatherer(tickers).get_dicts()

storage = DataStorage()

storage.clear()

for dict in dicts:
    storage.insert(dict)

# none is [1703]
