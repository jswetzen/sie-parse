#!/usr/bin/env python3
"""Output a SIE file that can be imported to Visma"""

import os
import sys
import calendar
import csv
from accounting_data import SieData, Verification, Transaction, DataField

def split_csv(table_file='TABELLER/Petra_Tabell.csv'):
    """Split account, cost center and project into three tables"""
    account = []
    cost_center = []
    account_project = []
    with open(table_file, newline='') as tablefile:
        tablereader = csv.reader(tablefile, delimiter=';')
        for row in tablereader:
            if row[0] != '' and row[1] != '':
                account.append([row[0], row[1]])
            if row[3] != '' and row[4] != '':
                cost_center.append([row[3], row[4]])
            if row[6] != '' and row[7] != '':
                account_project.append([row[6], row[7]])
    with open('TABELLER/P_Konto.csv', 'w', newline='') as accountfile:
        accountwriter = csv.writer(accountfile, delimiter=';')
        for row in account:
            accountwriter.writerow(row)
    with open('TABELLER/P_Costcenter.csv', 'w', newline='') as ccfile:
        ccwriter = csv.writer(ccfile, delimiter=';')
        for row in cost_center:
            ccwriter.writerow(row)
    with open('TABELLER/P_Konto_Projekt.csv', 'w', newline='') as projectfile:
        projectwriter = csv.writer(projectfile, delimiter=';')
        for row in account_project:
            projectwriter.writerow(row)

class PetraParser:
    """Form an output file based on an SieData object and translation table"""
    def __init__(self, petra_csv, account_file, cost_center_file, project_file,
                 default_petra_cc='3200'):
        self.petra_batches = []
        self.read_petra_csv(petra_csv)
        self.default_petra_cc = default_petra_cc
        self.parse_tables(account_file, cost_center_file, project_file)
        self.table = []

    def parse_tables(self, account_file, cost_center_file, account_project_file):
        """Read account, cost center and project translations from csv files"""
        self.account = {}
        self.cost_center = {}
        self.account_project = {}
        with open(account_file) as account:
            account_reader = csv.reader(account, delimiter=';')
            header = account_reader.__next__()
            if header[0] == 'P_Kto':
                for row in account_reader:
                    self.account[row[0]] = row[1]
            else:
                for row in account:
                    self.account[row[1]] = row[0]
        with open(cost_center_file) as cost_center:
            cost_center_reader = csv.reader(cost_center, delimiter=';')
            header = cost_center_reader.__next__()
            if header[0] == 'P_Kst':
                for row in cost_center_reader:
                    self.cost_center[row[0]] = row[1]
            else:
                for row in cost_center_reader:
                    self.cost_center[row[1]] = row[0]
        with open(account_project_file) as account_project:
            project_reader = csv.reader(account_project, delimiter=';')
            header = project_reader.__next__()
            if header[0] == 'P_Kst_P':
                for row in project_reader:
                    self.account_project[row[0]] = row[1]
            else:
                for row in project_reader:
                    self.account_project[row[1]] = row[0]

    def read_petra_csv(self, petra_csv):
        """Reads a petra csv export"""
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
                        kontonr = self.account[trans[2]]
                    objekt = ['1', self.cost_center[trans[1]]]
                    if trans[1] in self.account_project:
                        objekt.append('6')
                        objekt.append(self.account_project[trans[1]])
                    # TODO: verify that belopp has correct number of decimals
                    belopp = float(trans[6].replace(',', '.')) - float(trans[7].replace(',', '.'))
                    transdat = trans[5][6:10] + trans[5][3:5] + trans[5][:2]
                    transtext = trans[3]
                    transaction = Transaction(kontonr, objekt, belopp, transdat, transtext)
                    ver.add_trans(transaction)
                sie_data.add_data("#VER", ver)
        return sie_data

    def print_output(self):
        """Print petra batches to stdout"""
        for batch in self.petra_batches:
            print('B:', batch['data'][1:])
            for journal in batch['journals']:
                print('J:', journal['data'][1:])
                for transaction in journal['transactions']:
                    print('T:', transaction[1:])

    def  write_output(self, filename=None, overwrite=False):
        """Write csv to file, abort if it already exists"""
        writemode = 'w' if overwrite else 'x'
        # filename = 'Verifikationer_till_Petra_' + self.ver_month + '.csv'
        try:
            for encoding in ['utf_8_sig']:
                if not filename:
                    filename = 'CSV/PYTHON/VtP_' + self.ver_month + encoding + '.csv'
                try:
                    with open(filename, writemode, newline='', encoding=encoding) as csvfile:
                        csvwriter = csv.writer(csvfile, delimiter=';')
                        csvwriter.writerows(self.table)
                    # print("Encoding with ", encoding, "successful!")
                except UnicodeEncodeError as err:
                    print("Encoding failed: ", err)
                    os.remove(filename)
        except FileExistsError:
            sys.exit("Kan inte skriva " + filename + ", filen finns redan.")

if __name__ == "__main__":
    split_csv()
    P_PARSER = PetraParser('Petra-Visma/P_t_V_201704_2.txt', 'TABELLER/P_Konto.csv',
            'TABELLER/P_Costcenter.csv', 'TABELLER/P_Konto_Projekt.csv')
    SIE_DATA = P_PARSER.make_sie_data()
    print(SIE_DATA)
    # P_PARSER.print_output()
