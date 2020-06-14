from FileGatherer import FileGatherer
from DataStorage import DataStorage
import pandas as pd

# ticker_csv = pd.read_csv("constituents_csv.csv")["Symbol"]
# tickers = []
# for ticker in ticker_csv:
#     tickers.append(ticker)
#
# tickers = tickers[4:10]
#
# storage = DataStorage()
#
# for ticker in tickers:
#     dicts = FileGatherer([ticker]).get_dicts()
#     for dict in dicts:
#         storage.insert(dict)

f = FileGatherer(["ABMD"]).get_txts()

for i, fs in enumerate(f):
    print(f"{i}: {fs}")
