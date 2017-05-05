#!/usr/bin/env python3
"""Output a CSV file that can be imported to Petra"""

import os
import sys
import calendar
import csv

DEFAULT_PETRA_CC = '3200'
CODECS = [
    "ascii",
    "big5",
    "big5hkscs",
    "cp037",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb2312",
    "gbk",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "johab",
    "koi8_r",
    "koi8_u",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "utf_32",
    "utf_32_be",
    "utf_32_le",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "utf_8",
    "utf_8_sig"]

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
    Cost center is preceeded by a '1' and project by a '6', but the order
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
    def __init__(self, sie_data, account_file, cost_center_file, project_file):
        self.sie_data = sie_data
        self.parse_tables(account_file, cost_center_file, project_file)
        self.table = []
        self.ver_month = None

    def parse_tables(self, account_file, cost_center_file, project_file):
        """Read account, cost center and project translations from csv files"""
        self.account = {}
        self.cost_center = {}
        self.project = {}
        with open(account_file) as account:
            account_reader = csv.reader(account, delimiter=';')
            header = account_reader.__next__()
            if header[0] == 'V_Kto':
                for row in account_reader:
                    self.account[row[0]] = row[1]
            else:
                for row in account:
                    self.account[row[1]] = row[0]
        with open(cost_center_file) as cost_center:
            cost_center_reader = csv.reader(cost_center, delimiter=';')
            header = cost_center_reader.__next__()
            if header[0] == 'V_Kst':
                for row in cost_center_reader:
                    self.cost_center[row[0]] = row[1]
            else:
                for row in cost_center_reader:
                    self.cost_center[row[1]] = row[0]
        with open(project_file) as project:
            project_reader = csv.reader(project, delimiter=';')
            header = project_reader.__next__()
            if header[0] == 'V_Proj':
                for row in project_reader:
                    self.project[row[0]] = row[1]
            else:
                for row in project_reader:
                    self.project[row[1]] = row[0]

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
        checksum = round(sum(ver.sum_debit() for ver in verifications), 2)
        day = calendar.monthrange(ver_date.year, ver_date.month)[1]
        last_date_month = "{}/{:02}/{}".format(day, ver_date.month, ver_date.year)

        self.table.append(['B', description, checksum, last_date_month, '', '', '',
                           ''])

        for ver in verifications:
            if not ver.in_balance():
                raise Exception('Inte i balans:', ver)
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
            ref = "Visma Ver {}{}".format(ver.serie, ver.vernr)
            text = "{} - {}".format(ref, ver.vertext)
            date = ver.verdatum.format("%d/%m/%Y")
            self.table.append(['J', text, 'GL', 'STD', 'SEK', '1', date, ''])
            self.table.append([''] * 8)

            narr = ver.vertext # Default

            for trans in ver.trans_list:
                (visma_cc, visma_proj) = _parse_trans_objects(trans.objekt)
                if not visma_proj or visma_proj == 'P-32000000': # Use visma_cc instead
                    if not visma_cc: # Use default
                        cc = DEFAULT_PETRA_CC
                    else:
                        try:
                            cc = self.cost_center[visma_cc]
                        except KeyError:
                            raise KeyError("Costcenter " + visma_cc + " saknas i tabellen.")
                else:
                    try:
                        cc = self.project[visma_proj]
                    except KeyError:
                        raise KeyError("Projekt " + visma_proj + " saknas i tabellen.")
                try:
                    acct = self.account[trans.kontonr]
                except KeyError:
                    sys.exit("Konto " + trans.kontonr + " saknas i tabellen.")
                if trans.transtext and trans.kvantitet:
                    kvantitet = format(trans.kvantitet, '.2f').rstrip('0').rstrip('.')
                    narr = "{} {}".format(trans.transtext, kvantitet)
                elif trans.transtext:
                    narr = trans.transtext
                dt = trans.debit
                ct = trans.credit
                self.table.append(['T', cc, acct, narr, ref, date, dt, ct])
            self.table.append([''] * 8)

    def print_output(self):
        """Print csv output to stdout"""
        print("\n".join(','.join(str(r) for r in row) for row in self.table))

    def  write_output(self):
        """Write csv to file, abort if it already exists"""
        # filename = 'Verifikationer_till_Petra_' + self.ver_month + '.csv'
        try:
            for encoding in CODECS:
                filename = 'csv/Verifikationer_till_Petra_' + self.ver_month + encoding + '.csv'
                try:
                    with open(filename, 'w', newline='', encoding=encoding) as csvfile:
                        csvwriter = csv.writer(csvfile, delimiter=';')
                        csvwriter.writerows(self.table)
                    print("Encoding with ", encoding, "successful!")
                except UnicodeEncodeError as err:
                    print("Encoding failed: ", err)
                    os.remove(filename)
        except FileExistsError:
            sys.exit("Kan inte skriva " + filename + ", filen finns redan.")
