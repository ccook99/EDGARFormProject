import pandas as pd

from FileParser import FileParser


class DataConversion:
    def __init__(self, dictionary):
        self.dict = dictionary["transactions"]
        self.converted = self.convertDict(self.dict)

    def convertDict(self, dictionary):
        df = pd.DataFrame.from_dict(dictionary)

        return df

    def get_converted(self):
        return self.converted


fileUrl = "https://www.sec.gov/Archives/edgar/data/1182464/000120919120025998/0001209191-20-025998.txt"

file = FileParser(fileUrl).get_data()

print(DataConversion(file).get_converted().to_string())
