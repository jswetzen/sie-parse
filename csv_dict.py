#!/usr/bin/env python3
"""Access a csv file using a dictionary interface."""

import collections
import csv

class CSVKeyMissing(KeyError):
    def __init__(self, message, csv_dict, key):
        super().__init__(message)
        self.csv_dict = csv_dict
        self.key = key


class CSVDict(collections.MutableMapping):
    """
    Access a csv file using a dictionary interface.
    Obvious flaws include utter failure if the csv is modified while it's being
    used by Python. Still, it should be useful.
    It will just die if the csv file is missing or lacks a header line.
    """
    def __init__(self, csv_filename):
        self.store = dict()
        self.csv_filename = csv_filename
        with open(self.csv_filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            self.fields = csv_reader.__next__()
            for row in csv_reader:
                self.store[row[0]] = {}
                for i in range(min(len(self.fields), len(row)) - 1):
                    self.store[row[0]][self.fields[i + 1]] = row[i + 1]

    def __getitem__(self, key):
        try:
            return self.store[key]
        except KeyError:
            raise CSVKeyMissing("Key {} missing".format(key), self, key)

    def __setitem__(self, key, value):
        if key in self.store:
            self.__delitem__(key)
        # Write to csv file
        with open(self.csv_filename, 'a', newline='') as csv_file:
            if isinstance(value, dict):
                value[self.fields[0]] = key
                values = list([value.get(k, '') for k in self.fields])
            elif isinstance(value, list):
                values = [key] + value
            else:
                values = [key, value] + [''] * (len(self.fields) - 2)
            values += [''] * (len(self.fields) - len(values))

            csv_writer = csv.writer(csv_file, delimiter=';',
                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(values)

            self.store[key] = dict(zip(self.fields[1:], values[1:]))

    def __delitem__(self, key):
        with open(self.csv_filename, 'r+', newline='') as csv_file:
            data = csv_file.readlines()
            csv_file.seek(0)
            for line in data:
                if not line.startswith(key):
                    csv_file.write(line)
            csv_file.truncate()
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
