from pymongo import MongoClient

class DataStorage:
    '''
    Used as an API to access a locally run MongoDB.
    '''
    def __init__(self):
        '''
        Used to create a MongoDB API.
        '''
        self.client = MongoClient()
        self.db = self.client.EDGARProject
        self.collection = self.db.Filings

    def insert(self, dict):
        '''
        Used to insert a dictionary object as a document into MongoDB.
        :param dict: The dictionary to be inserted.
        '''
        self.collection.insert(dict)

    def clear(self):
        '''
        Used to flush the entire MongoDB.
        '''
        self.collection.drop()