import requests
from urllib import parse
from bs4 import BeautifulSoup


def getFirstUrl(ticker):
    params = {'ticker': ticker,
              'owner': 'only',
              'type': '4',
              'action': 'getcompany',
              'start': '0',
              'count': '100',
              'output': 'atom'}

    qs = parse.urlencode(params)
    url = "https://www.sec.gov/cgi-bin/browse-edgar" + "?" + qs
    return url


def getNextUrl(url):
    nextUrlResp = requests.get(url, timeout=5)
    nextUrlResp.close()
    soup = BeautifulSoup(nextUrlResp.text, "html.parser")
    soup.encode("utf-8")
    next = soup.find("link", {"rel" : "next"})
    if next is None:
        return "End"
    return next['href']

def getAllUrls(ticker):
    urls = []

    first = getFirstUrl(ticker)
    urls.append(first)
    # while


# Collects files and stores them in a DataStorage object
class FileGatherer:

    # storage: the storage object data is stored in
    # tickers: the tickers data will be retrieved from
    # form: the form data will be pulled from (only "4" for now)
    def __init__(self, tickers):
        self.tickers = tickers
        self.data = self.gather_data(self.tickers)

    def gather_data(self, tickers):
        urls = []
        for ticker in tickers:
            pass


first = getFirstUrl("TSLA")
next = getNextUrl(first)
print(first)
print(next)