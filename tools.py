#!/usr/bin/env python3
"""Various tools used to translate files etc. Mostly used once only."""

import csv
from accounting_data import SieData, SieField, Verification, Transaction, DataField, SieIO
from csv_dict import CSVDict, CSVKeyMissing

def add_accounts_from_sie(sie_data, account_file):
    """Take #KONTO, #SRU and #KTYP from SieData and add to account_file csv"""
    konto = CSVDict(account_file)
    for key in ['KONTO', 'SRU', 'KTYP']:
        for entry in sie_data.data['#' + key]:
            if entry.data[0] in konto and len(entry.data) > 1:
                konto[entry.data[0]][key] = entry.data[1]

    # To get the csv updated, not just changing the objects
    for k, v in konto.items():
        konto[k] = v

def add_objects_from_sie(sie_data, sie_objects_1, sie_objects_6):
    """Take object names from SieData and store in csv tables."""
    objects = {'1': CSVDict(sie_objects_1), '6': CSVDict(sie_objects_6)}
    for entry in sie_data.data['#OBJEKT']:
        objects[entry.data[0]][entry.data[1]] = entry.data[2]


def complement_from_SIE(siecsv, tablecsv):
    obj = CSVDict(siecsv)
    table = CSVDict(tablecsv)
    for v, data in table.items():
        if v in obj:
            data['Name'] = obj[v]['Name']
            table[v] = data

if __name__ == "__main__":
    complement_Re_CC()
    complement_Proj_CC()
