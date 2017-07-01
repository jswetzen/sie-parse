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


def complement_Re_CC():
    with open('TABELLER/Re_CC.csv', 'r') as re_cc, open('TABELLER/Re_CC_2.csv', 'w') as re_cc_2:
        obj1 = CSVDict('TABELLER/SIE_objects_1.csv')
        re_cc_reader = csv.reader(re_cc, delimiter=';')
        re_cc_reader.__next__()
        re_cc_2.write("V_Kst;Name;P_CC\n")
        for row in re_cc_reader:
            try:
                re_cc_2.write(';'.join([row[0], obj1[row[0]]['Name'], row[1]]))
                re_cc_2.write("\n")
            except CSVKeyMissing as csverr:
                re_cc_2.write(';'.join([row[0], '', row[1]]))
                re_cc_2.write("\n")
                print(csverr)

def complement_Proj_CC():
    with open('TABELLER/Proj_CC.csv', 'r') as proj_cc, open('TABELLER/Proj_CC_2.csv', 'w') as proj_cc_2:
        obj6 = CSVDict('TABELLER/SIE_objects_6.csv')
        proj_cc_reader = csv.reader(proj_cc, delimiter=';')
        proj_cc_reader.__next__()
        proj_cc_2.write("V_Proj;Name;P_CC\n")
        for row in proj_cc_reader:
            try:
                proj_cc_2.write(';'.join([row[0], obj6[row[0]]['Name'], row[1]]))
                proj_cc_2.write("\n")
            except CSVKeyMissing as csverr:
                proj_cc_2.write(';'.join([row[0], '', row[1]]))
                proj_cc_2.write("\n")
                print(csverr)

if __name__ == "__main__":
    complement_Re_CC()
    complement_Proj_CC()
