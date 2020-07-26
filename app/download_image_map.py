#!/usr/bin/env python
import csv


class Parser():
    def __init__(self, csv_file=None):
        self._parsed_data = None
        self.csv_file = csv_file
        # other useful things here

    @property
    def parsed_data(self):
        if self._parsed_data is not None:
            return self._parsed_data
        self._parsed_data = self.get_data()
        return self._parsed_data

    def transform_csv_data(self, data):
        transformed = {}
        key = ""
        for line in data:
            try:
                key = '/'.join(line[0:2])
                transformed[key] = '/'.join(line[2:5])
            except IndexError as e:
                print("Missing fields in data '{0}'. Error: '{1}'".format(line, e))
                break
        return transformed

    def import_csv(self):
        with open(self.csv_file) as f:
            csvreader = csv.reader(f, delimiter='/')
            data = list(csvreader)
        return data

    def get_data(self):
        data = self.import_csv()
        return self.transform_csv_data(data)

    def reload(self):
        self._parsed_data = None
        self.get_data()
        return self.parsed_data
