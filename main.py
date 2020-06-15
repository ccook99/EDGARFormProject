from FileGatherer import FileGatherer
from DataStorage import DataStorage
import pandas as pd

ticker_csv = pd.read_csv("constituents_csv.csv")["Symbol"]
tickers = []
for ticker in ticker_csv:
    tickers.append(ticker)

tickers = tickers[3:10]

storage = DataStorage()

for ticker in tickers:
    # create gathering object
    f = FileGatherer([ticker])

    # load dictionaries of xml
    f.load_dicts()

    # pull dictionaries
    dicts = f.get_dicts()

    # insert dictionaries into mongo
    for dict in dicts:
        storage.insert(dict)

    # move data into dataframes
    data_df = pd.DataFrame(f.get_data())
    txts_df = pd.DataFrame(f.get_txts())
    dicts_df = pd.DataFrame(f.get_dicts())
    nones_df = pd.DataFrame(f.get_nones())

    # push dataframes into csvs
    data_df.to_csv(f"data/{ticker}_data.csv")
    txts_df.to_csv(f"data/{ticker}_txts.csv")
    dicts_df.to_csv(f"data/{ticker}_dicts.csv")
    nones_df.to_csv(f"data/{ticker}_nones.csv")

# for i, fs in enumerate(d):
#     print(f"{i}: {fs}")
#
# print(n)
