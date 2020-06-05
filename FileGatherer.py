import requests
from urllib import parse
from bs4 import BeautifulSoup
import xmltodict


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
    next = soup.find("link", {"rel": "next"})
    if next is None:
        return "End"
    return next['href']


def getAllUrls(ticker):
    urlsInit = []

    first = getFirstUrl(ticker)
    urlsInit.append(first)
    return getRestUrls(urlsInit, first)


def getRestUrls(urlsOld, url):
    nextUrl = getNextUrl(url)
    if nextUrl != "End":
        urlsOld.append(nextUrl)
        return getRestUrls(urlsOld, nextUrl)
    else:
        return urlsOld


# Collects files and stores them in a DataStorage object
class FileGatherer:

    # storage: the storage object data is stored in
    # tickers: the tickers data will be retrieved from
    # form: the form data will be pulled from (only "4" for now)
    def __init__(self, tickers):
        self.tickers = tickers
        self.data = self.gather_data(self.tickers)
        self.txts = self.convert_htm_txt(self.data)
        self.dicts = self.convert_txt_dicts(self.txts)

    def get_data(self):
        return self.data

    def gather_data(self, tickers):
        htms = []
        for ticker in tickers:
            urls = getAllUrls(ticker)
            for url in urls:
                page = requests.get(url)
                page.close()
                soup = BeautifulSoup(page.content, "xml")
                entries = soup.findAll("entry")
                for entry in entries:
                    htms.append(entry.find("filing-href").string)
        return htms

    def convert_htm_txt(self, htms):
        txts = []
        for htm in htms:
            txts.append(htm.replace("-index.htm", ".txt"))
        return txts

    def convert_txt_dicts(self, txts):
        dicts = []
        tot = len(txts)
        i = 0
        for txt in txts:
            if i % 10 == 0:
                print(f"{i}/{tot} completed so far")
            i = i + 1
            resp = requests.get(txt)
            resp.close()
            soup = BeautifulSoup(resp.text, "lxml")
            #soup.encode("utf-8")
            od = soup.find("ownershipdocument")
            #print(od.prettify())
            d = xmltodict.parse(od.prettify())
            dicts.append(d)
        return dicts

print(FileGatherer(["TSLA"]).dicts)