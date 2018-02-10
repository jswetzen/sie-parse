#!/usr/bin/env python3
"""Output a CSV file that can be imported to Petra"""

import os
import sys
import calendar
import csv
from csv_dict import CSVDict, CSVKeyMissing

def split_csv(table_file='Tabell.csv'):
    """Split account, cost center and project into three tables"""
    account = []
    cost_center = []
    project = []
    with open(table_file, newline='') as tablefile:
        tablereader = csv.reader(tablefile, delimiter=';')
        for row in tablereader:
            if row[0] != '' and row[1] != '':
                account.append([row[0], row[1]])
            if row[3] != '' and row[4] != '':
                cost_center.append([row[3], row[4]])
            if row[6] != '' and row[7] != '':
                project.append([row[6], row[7]])
    with open('Konto.csv', 'w', newline='') as accountfile:
        accountwriter = csv.writer(accountfile, delimiter=';')
        for row in account:
            accountwriter.writerow(row)
    with open('Costcenter.csv', 'w', newline='') as ccfile:
        ccwriter = csv.writer(ccfile, delimiter=';')
        for row in cost_center:
            ccwriter.writerow(row)
    with open('Projekt.csv', 'w', newline='') as projectfile:
        projectwriter = csv.writer(projectfile, delimiter=';')
        for row in project:
            projectwriter.writerow(row)

def _parse_trans_objects(trans):
    """
    Handle an object list of a transaction.
    The object list contains a cost center and project, formatted like so
    ['1', 'K0000', '6', 'P-00000000'].
    Cost center (resultatenhet) is preceeded by a '1' and project by a '6', but the order
    of the two could be reversed. Cost center always begins with 'K' and
    project with 'P-'. The object list could also be empty.

    Returns a tuple (cost_center, project), where any of the two could be
    None in case the information is missing from the object list.
    """
    cost_center = project = None
    trans_it = iter(trans)
    for idx in trans_it:
        obj = next(trans_it)
        if idx == '1' and obj.startswith('K'):
            cost_center = obj
        elif idx == '6' and obj.startswith('P-'):
            project = obj
    return (cost_center, project)

class PetraOutput:
    """Form an output file based on an SieData object and translation table"""
    def __init__(self, sie_data, account_file, cost_center_file, project_file,
                 default_petra_cc='3200'):
        self.sie_data = sie_data
        self.default_petra_cc = default_petra_cc

        # self.parse_tables(account_file, cost_center_file, project_file)
        self.account = CSVDict(account_file)
        self.cost_center = CSVDict(cost_center_file)
        self.project = CSVDict(project_file)

        self.table = []
        self.ver_month = None

    def populate_output_table(self):
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        # pylint: disable=invalid-name
        """Extract interesting informatin from the Sie data and form output"""
        header = ['', 'CC', 'Account', 'Narrative', 'Reference', 'Date', 'Dt',
                  'Ct']
        self.table.append(header)

        program = self.sie_data.get_data('#PROGRAM')[0].data[0].split()[0]
        verifications = self.sie_data.get_data('#VER')
        ver_date = next(v.verdatum for v in verifications if v.verdatum.has_date)
        self.ver_month = ver_date.format("%Y-%m")
        description = "Imported from {} {}".format(program, self.ver_month)
        checksum = format(sum(ver.sum_debit() for ver in verifications),
                '.2f').rstrip('0').rstrip('.').replace('.',',')
        day = calendar.monthrange(ver_date.year, ver_date.month)[1]
        last_date_month = "{}/{:02}/{}".format(day, ver_date.month, ver_date.year)

        self.table.append(['B', description, checksum, last_date_month, '', '', '',
                           ''])

        for ver in verifications:
            if not ver.in_balance():
                raise Exception('Inte i balans:', ver)
            """
            # Contains 'Swetzén'
            if ver.serie == 'A' and ver.vernr == '170071':
                print(ver)
            # Contains stange characters
            if ver.serie == 'C' and ver.vernr == '170058':
                print(ver)
            # CC with 'XXXX'
            if ver.serie == 'C' and ver.vernr == '170064':
                print(ver)
            # Rounding error?
            if ver.serie == 'C' and ver.vernr == '170067':
                print(ver)
            """
            ref = "Visma Ver {}{}".format(ver.serie, ver.vernr)
            text = "{} - {}".format(ref, ver.vertext)
            date = ver.verdatum.format("%d/%m/%Y")
            self.table.append(['J', text, 'GL', 'STD', 'SEK', '1', date, ''])

            narr = ver.vertext # Default

            for trans in ver.trans_list:
                (visma_cc, visma_proj) = _parse_trans_objects(trans.objekt)
                if not visma_proj or visma_proj == 'P-32000000': # Use visma_cc instead
                    if not visma_cc: # Use default
                        cc = self.default_petra_cc
                    else:
                        cc = self.cost_center[str(visma_cc)]['P_CC']
                else:
                    cc = self.project[str(visma_proj)]['P_CC']
                acct = self.account[str(trans.kontonr)]['P_Acct']
                if trans.transtext and trans.kvantitet:
                    kvantitet = format(trans.kvantitet,
                            '.2f').rstrip('0').rstrip('.').replace('.',',')
                    narr = "{} {}".format(trans.transtext, kvantitet)
                elif trans.transtext:
                    narr = trans.transtext
                dt = trans.debit
                ct = trans.credit
                self.table.append(['T', cc, acct, narr, ref, date, dt, ct])

    def print_output(self):
        """Print csv output to stdout"""
        print("\n".join(','.join(str(r) for r in row) for row in self.table))

    def  write_output(self, filename=None, overwrite=False):
        """Write csv to file, abort if it already exists"""
        writemode = 'w' if overwrite else 'x'
        try:
            for encoding in ['utf_8']:
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
