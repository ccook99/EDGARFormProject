from pymongo import MongoClient
from FileGatherer import FileGatherer

class DataStorage:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.EDGARProject
        self.collection = self.db.Filings

