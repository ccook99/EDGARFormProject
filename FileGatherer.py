import requests
from urllib import parse
from bs4 import BeautifulSoup
import xmltodict
from ratelimit import limits, sleep_and_retry

nones = []


def getFirstUrl(ticker):
    '''
    Obtains the first url for a ticker's RSS feed with correct filters.
    :param ticker: The ticker to get the url for.
    :return: The url of the first page of the RSS feed.
    '''
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
    '''
    Converts the .htm urls to the corresponding .txt files.
    :param htms: List of .htm urls.
    :return: List of .txt urls.
    '''
    txts = []
    for htm in htms:
        txts.append(htm.replace("-index.htm", ".txt"))
    return txts


class FileGatherer:
    '''
    Used to gather dictionary versions of Form 4 xml documents on the EDGAR public database.
    '''

    def __init__(self, tickers):
        self.tickers = tickers
        self.data = None
        self.txts = None
        self.dicts = None
        self.nones = {}

    def load_data(self):
        '''
        Loads the .htm urls for each entry of the RSS filing feed.
        '''
        self.data = self.gather_data(self.tickers)

    def load_txts(self):
        '''
        Loads the .txt urls for each entry of the RSS filing feed.
        '''
        if self.data is None:
            self.load_data()
        self.txts = convert_htm_txt(self.data)

    def load_dicts(self):
        '''
        Loads the dictionary versions of all gathered XML form 4 documents.
        '''
        if self.txts is None:
            self.load_txts()
        self.dicts = self.convert_txt_dicts(self.txts)

    def get_data(self):
        '''
        Used to retrieve the .htm urls.
        :return: List of .htm urls.
        '''
        return self.data

    def get_txts(self):
        '''
        Used to retrieve the .txt urls.
        :return: List of .txt urls.
        '''
        return self.txts

    def get_dicts(self):
        '''
        Used to retrieve the dictionaries of the form 4 documents.
        :return: List of form 4 dictionaries.
        '''
        return self.dicts

    def get_nones(self):
        '''
        Used for troubleshooting.
        :return: List of indexes where the xml document could not be pulled for whatever reason.
        '''
        return self.nones

    def gather_data(self, tickers):
        '''
        Used to gather the .htm urls for each individual filing filed during or after 2010.
        :param tickers: The tickers to gather the urls from.
        :return: List of form 4 .htm urls for the given tickers.
        '''
        htms = []
        ticker_len = len(tickers)
        for ticker_index, ticker in enumerate(tickers):
            urls = self.getAllUrls(ticker)
            url_len = len(urls)
            for url_index, url in enumerate(urls):
                print(f"ticker ({ticker}): {ticker_index + 1}/{ticker_len} --- rss feed: {url_index + 1}/{url_len}")
                page = self.access_api(url)
                soup = BeautifulSoup(page.content, "xml")
                entries = soup.findAll("entry")
                for entry in entries:
                    if int(entry.find("filing-date").string[:4]) >= 2010:
                        htms.append(entry.find("filing-href").string)
        return htms

    def convert_txt_dicts(self, txts):
        '''
        Used to parse the xml in .txt urls and convert to Python dictionaries.
        :param txts: The list of .txt urls to be parsed.
        :return: List of form 4 dictionaries.
        '''
        dicts = []
        txts_len = len(txts)
        for txt_index, txt in enumerate(txts):
            print(f"dict: {txt_index + 1}/{txts_len}")
            resp = self.access_api(txt)
            soup = BeautifulSoup(resp.text, "lxml")
            od = soup.find("ownershipdocument")
            if od is not None:  # if the response was what was expected
                d = xmltodict.parse(od.prettify())
                dicts.append(d)
            else:  # if the response was something unexpected, try again
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
        '''
        Used to retrieve the urls of a ticker's RSS feed because the feeds normally spanned multiple pages.
        :param ticker: the ticker to get the RSS urls of
        :return: a list of RSS urls
        '''
        urlsInit = []

        first = getFirstUrl(ticker)
        urlsInit.append(first)
        return self.getRestUrls(urlsInit, first)

    def getNextUrl(self, url):
        '''
        Used to find the next RSS url given an RSS url.
        :param url: The url to search for the next RSS page.
        :return: The url to the next page, or 'End' if the given url was the last of the RSS feed.
        '''
        nextUrlResp = self.access_api(url)
        soup = BeautifulSoup(nextUrlResp.text, "html.parser")
        soup.encode("utf-8")
        next = soup.find("link", {"rel": "next"})
        if next is None:
            return "End"
        return next['href']

    def getRestUrls(self, urlsOld, url):
        '''
        Used as a helper function to retrieve RSS urls recursively.
        :param urlsOld: The list of urls passed from previous calls.
        :param url: The url used to find the next url if it exists.
        :return: List of all urls of an RSS feed, or a recursive call until this was found.
        '''
        nextUrl = self.getNextUrl(url)
        if nextUrl != "End":
            urlsOld.append(nextUrl)
            return self.getRestUrls(urlsOld, nextUrl)
        else:
            return urlsOld

    @sleep_and_retry
    @limits(calls=10, period=1)
    def access_api(self, url):
        '''
        Used to limit EDGAR API calls to 10 calls/second.
        :param url: The url to retrieve a response from.
        :return: The response from the given url.
        '''
        resp = requests.get(url)
        return resp
