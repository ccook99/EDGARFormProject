import requests
from urllib import parse
from bs4 import BeautifulSoup
from datetime import datetime
import xmltodict
from ratelimit import limits, sleep_and_retry

nones = []


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


def convert_htm_txt(htms):
    txts = []
    for htm in htms:
        txts.append(htm.replace("-index.htm", ".txt"))
    return txts


class FileGatherer:

    def __init__(self, tickers):
        self.tickers = tickers
        self.data = None
        self.txts = None
        self.dicts = None
        self.nones = {}

    def load_data(self):
        self.data = self.gather_data(self.tickers)

    def load_txts(self):
        if self.data is None:
            self.load_data()
        self.txts = convert_htm_txt(self.data)

    def load_dicts(self):
        if self.txts is None:
            self.load_txts()
        self.dicts = self.convert_txt_dicts(self.txts)

    def get_data(self):
        return self.data

    def get_dicts(self):
        return self.dicts

    def get_txts(self):
        return self.txts

    def get_nones(self):
        return self.nones

    def gather_data(self, tickers):
        htms = []
        ticker_len = len(tickers)
        for ticker_index, ticker in enumerate(tickers):
            urls = self.getAllUrls(ticker)
            url_len = len(urls)
            for url_index, url in enumerate(urls):
                print(f"ticker ({ticker}): {ticker_index+1}/{ticker_len} --- rss feed: {url_index+1}/{url_len}")
                page = self.access_api(url)
                soup = BeautifulSoup(page.content, "xml")
                entries = soup.findAll("entry")
                for entry in entries:
                    if int(entry.find("filing-date").string[:4]) >= 2010:
                        htms.append(entry.find("filing-href").string)
        return htms

    def convert_txt_dicts(self, txts):
        dicts = []
        txts_len = len(txts)
        for txt_index, txt in enumerate(txts):
            print(f"dict: {txt_index+1}/{txts_len}")
            resp = self.access_api(txt)
            soup = BeautifulSoup(resp.text, "lxml")
            # soup.encode("utf-8")
            od = soup.find("ownershipdocument")
            # print(od.prettify())
            if od is not None:
                d = xmltodict.parse(od.prettify())
                dicts.append(d)
            else:
                od2 = soup.find("ownershipdocument")
                if od2 is not None:
                    d = xmltodict.parse(od2.prettify())
                    dicts.append(d)
                else:
                    self.nones[soup.find("issuerTradingSymbol").string].append(txt_index)
                    nones.append(txt_index)
        print(nones)
        return dicts

    def getAllUrls(self, ticker):
        urlsInit = []

        first = getFirstUrl(ticker)
        urlsInit.append(first)
        return self.getRestUrls(urlsInit, first)

    def getNextUrl(self, url):
        nextUrlResp = self.access_api(url)
        soup = BeautifulSoup(nextUrlResp.text, "html.parser")
        soup.encode("utf-8")
        next = soup.find("link", {"rel": "next"})
        if next is None:
            return "End"
        return next['href']

    def getRestUrls(self, urlsOld, url):
        nextUrl = self.getNextUrl(url)
        if nextUrl != "End":
            urlsOld.append(nextUrl)
            return self.getRestUrls(urlsOld, nextUrl)
        else:
            return urlsOld

    @sleep_and_retry
    @limits(calls=10, period=1)
    def access_api(self, url):
        resp = requests.get(url)
        return resp


# f = FileGatherer(["TSLA"]).dicts
#
#
# print(f)

"""
11 calls/second (SnR) - 0:00:48.878691, 0:00:48.152967, 0:00:48.959893
datetime.timedelta(seconds=58, microseconds=53473), 
datetime.timedelta(seconds=49, microseconds=534706), 
datetime.timedelta(seconds=50, microseconds=129737), 
datetime.timedelta(seconds=50, microseconds=361094), 
datetime.timedelta(seconds=56, microseconds=659028), 
datetime.timedelta(seconds=45, microseconds=995785), 
datetime.timedelta(seconds=48, microseconds=355709), 
datetime.timedelta(seconds=49, microseconds=319261), 
datetime.timedelta(seconds=50, microseconds=757648), 
datetime.timedelta(seconds=48, microseconds=80713)
10 calls/second (SnR) - 0:01:00.809511, 0:00:53.710170, 0:00:54.697445
9  calls/second (SnR) - 0:01:00.707073, 0:00:57.804717, 0:01:03.107277
"""
