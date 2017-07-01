#!/usr/bin/env python3
"""Output a SIE file that can be imported to Visma"""

import os
import sys
import csv
from datetime import datetime
from accounting_data import SieData, SieField, Verification, Transaction, DataField, SieIO
from csv_dict import CSVDict

class PetraParser:
    """Form an output file based on an SieData object and translation table"""
    def __init__(self, petra_csv, acct_kto_file, cc_re_proj_file, sie_defaults_file,
            sie_dims_file, sie_units_file, kto_acct_file, re_cc_file, proj_cc_file,
            default_petra_cc='3200'):
        self.sie_data = SieData()
        self.petra_batches = []
        self.read_petra_csv(petra_csv)
        self.default_petra_cc = default_petra_cc
        self.acct_kto = CSVDict(acct_kto_file)
        self.cc_re_proj = CSVDict(cc_re_proj_file)
        self.sie_defaults = CSVDict(sie_defaults_file)
        self.sie_dims = CSVDict(sie_dims_file)
        self.sie_units = CSVDict(sie_units_file)
        self.kto_acct = CSVDict(kto_acct_file)
        self.sie_objects = {'1': CSVDict(re_cc_file),
                            '6': CSVDict(proj_cc_file)}
        self.table = []

    def read_petra_csv(self, petra_csv):
        """Reads a petra csv export to self.petra_batches"""
        with open(petra_csv, 'r', encoding='latin1') as petra_csv_file:
            petra_reader = csv.reader(petra_csv_file, delimiter=';')
            batch = {}
            journal = {}
            for row in petra_reader:
                if row and row[0] == 'B':
                    if batch:
                        if journal:
                            batch['journals'].append(journal)
                            journal = {}
                        self.petra_batches.append(batch)
                    batch = {'data': row, 'journals': []}
                elif row and row[0] == 'J':
                    if journal:
                        batch['journals'].append(journal)
                    journal = {'data': row, 'transactions': []}
                elif row and row[0] == 'T':
                    journal['transactions'].append(row)
            if journal:
                batch['journals'].append(journal)
                self.petra_batches.append(batch)
    
    def make_sie_data(self):
        """Put Petra batches in a SieData object to be exported"""
        sie_data = SieData()

        for name, value in self.sie_defaults.items():
            sie_data.add_data(DataField(['#' + name] + value['Data'].split(',')))
        sie_data.add_data(SieField('#GEN', datetime.now().strftime("%Y%m%d")))

        for idx, data in self.sie_dims.items():
            sie_data.add_data(DataField(['#DIM', idx, data['Name']]))
        for idx, data in self.sie_units.items():
            sie_data.add_data(DataField(['#ENHET', idx, data['Name']]))
        for idx, data in self.kto_acct.items():
            for field in ['KONTO', 'KTYP', 'SRU']:
                if data[field]:
                    sie_data.add_data(DataField(['#' + field, idx, data[field]]))
        for dim in ['1', '6']:
            for idx, data in self.sie_objects[dim].items():
                sie_data.add_data(DataField(['#OBJEKT', dim, idx, data['Name']]))

        for batch in self.petra_batches:
            for journal in batch['journals']:
                serie = 'P'
                vernr = '0'
                transdat = journal['transactions'][0][5]
                verdatum = transdat[6:10] + transdat[3:5] + transdat[:2]
                vertext = journal['data'][1]
                ver = Verification(serie, vernr, verdatum, vertext, verdatum)
                for trans in journal['transactions']:
                    # Non-swedish transactions have account 1998
                    if trans[1][:2] != '32' and trans[2] != '8500' and trans[2] != '5601':
                        kontonr = '1998'
                    else:
                        kontonr = self.acct_kto[trans[2]]['V_Kto']
                    objekt = ['1', self.cc_re_proj[trans[1]]['V_Re'], '6',
                            self.cc_re_proj[trans[1]]['V_Proj']]
                    belopp = float(trans[6].replace(',', '.')) - float(trans[7].replace(',', '.'))
                    transdat = trans[5][6:10] + trans[5][3:5] + trans[5][:2]
                    transtext = trans[3]
                    transaction = Transaction(kontonr, objekt, belopp, transdat, transtext)
                    ver.add_trans(transaction)
                sie_data.add_data(ver)
        self.sie_data = sie_data

    def print_output(self):
        """Print petra batches to stdout"""
        for batch in self.petra_batches:
            print('B:', batch['data'][1:])
            for journal in batch['journals']:
                print('J:', journal['data'][1:])
                for transaction in journal['transactions']:
                    print('T:', transaction[1:])

if __name__ == "__main__":
    P_PARSER = PetraParser('Petra-Visma/P_t_V_201704_2.txt', 'TABELLER/Acct_Kto.csv',
            'TABELLER/CC_Re_Proj.csv', 'TABELLER/SIE_defaults.csv',
            'TABELLER/SIE_dims.csv', 'TABELLER/SIE_units.csv',
            'TABELLER/Kto_Acct.csv', 'TABELLER/Re_CC.csv',
            'TABELLER/Proj_CC.csv')
    P_PARSER.make_sie_data()
    if not P_PARSER.sie_data.is_complete():
        print("Något saknas i SIE-filen")
    else:
        SieIO.writeSie(P_PARSER.sie_data, 'Petra-Visma/PtV_test.SI', True)
    print(P_PARSER.sie_data)
