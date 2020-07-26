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
        row_counter = 0
        for line in data:
            try:
                row_counter = row_counter + 1
                key = line[0]
                transformed[key] = line[1]
            except IndexError as e:
                print("userdata.csv line {}: Malformed or Missing fields in data '{}'. Error: '{}'".format(row_counter, line, e))
        return transformed

    def import_csv(self):
        with open(self.csv_file) as f:
            csvreader = csv.reader(f, delimiter='|')
            data = list(csvreader)
        return data

    def get_data(self):
        data = self.import_csv()
        return self.transform_csv_data(data)

    def reload(self):
        self._parsed_data = None
        self.get_data()
        return self.parsed_data
