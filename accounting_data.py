#!/usr/bin/env python3
"""Klasser för att lagra bokföringsdata från en SI-fil"""

from datetime import datetime
from collections import defaultdict

class SieData:
    """Lagrar datan som behövs i en SI-fil"""
    single_fields = ['#FLAGGA', '#PROGRAM', '#FORMAT', '#GEN', '#SIETYP',
                     '#FNAMN', '#ORGNR']
    needed_fields = ['#FLAGGA', '#PROGRAM', '#FORMAT', '#GEN', '#SIETYP',
                     '#FNAMN', '#KONTO']
    # Identifikationsposter
    ident_fields = ['#FLAGGA', '#PROGRAM', '#FORMAT', '#GEN', '#SIETYP',
                    '#PROSA', '#FTYP', '#FNR', '#ORGNR', '#BKOD', '#ADRESS',
                    '#FNAMN', '#RAR', '#TAXAR', '#OMFATTN', '#KPTYP',
                    '#VALUTA']
    # Kontoplansuppgifter
    account_fields = ['#KONTO', '#KTYP', '#ENHET', '#SRU', '#DIM', '#UNDERDIM',
                      '#OBJEKT']
    # Saldoposter/Verifikationsposter
    balance_fields = ['#IB', '#UB', '#OIB', '#OUB', '#RES', '#PSALDO',
                      '#PBUDGET', '#VER']
    # Kontrollsummeposter
    control_fields = ["#KSUMMA"]

    def __init__(self):
        self.data = defaultdict(list)

    def __repr__(self):
        fields = (self.ident_fields + self.account_fields + self.balance_fields
                  + self.control_fields)
        res = ''
        for field in fields:
            for line in self.data[field]:
                res += '{}\n'.format(line)

        return res

    def add_data(self, name, data):
        """Spara data för posten name. #VER läggs till en lista."""
        if name in self.single_fields and self.data[name]:
            raise ValueError("This field is set already: ", name)
        self.data[name].append(data)

    def get_data(self, name):
        """Läs data från posten name"""
        return self.data[name]

    def is_complete(self):
        """True om all information som specifikationen kräver är sparad"""
        return all([self.data[field] for field in self.needed_fields])

class Verification:
    """Lagrar datan för en verifikation"""
    def __init__(self, serie, vernr, verdatum, vertext='', regdatum='',
                 sign=''):
        # pylint: disable=too-many-arguments
        self.serie = serie
        self.vernr = vernr
        self.verdatum = MaybeDate(verdatum)
        self.vertext = vertext
        self.regdatum = MaybeDate(regdatum)
        self.sign = sign
        self.trans_list = []

    def __repr__(self):
        res = '#VER "{}" "{}" "{}" "{}" "{}" "{}"'.format(
            self.serie, self.vernr, self.verdatum, self.vertext,
            self.regdatum, self.sign)
        res += '\n{\n'
        for trans in self.trans_list:
            res += '   {}\n'.format(trans)
        res += '}'
        return res

    def add_trans(self, trans):
        """Lägg till en transaktion till verifikationen"""
        self.trans_list.append(trans)

    def is_complete(self):
        """True om det finns transaktioner inlagda"""
        return bool(self.trans_list)

    def in_balance(self):
        """True om summan av debit och kredit är noll"""
        return self.sum_debit() + self.sum_credit() == 0

    def sum_debit(self):
        """Addera alla positiva belopp"""
        return round(sum([trans.belopp for trans in self.trans_list
                          if trans.belopp > 0]), 2)

    def sum_credit(self):
        """Addera alla negativa belopp"""
        return round(sum([trans.belopp for trans in self.trans_list
                          if -1 * trans.belopp > 0]), 2)

class Transaction:
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Lagrar datan för en transaktion"""
    def __init__(self, kontonr, objekt, belopp, transdat='', transtext='',
                 kvantitet=0.0, sign=''):
        # pylint: disable=too-many-arguments
        self.kontonr = kontonr
        self.objekt = objekt
        self.belopp = float(belopp)
        self.transdat = MaybeDate(transdat)
        self.transtext = transtext
        self.kvantitet = float(kvantitet)
        self.sign = sign

        if self.belopp < 0:
            (self.credit, self.debit) = (format(-1*self.belopp, '.2f').rstrip('0').rstrip('.'), '')
        else:
            (self.credit, self.debit) = ('', format(self.belopp, '.2f').rstrip('0').rstrip('.'))

    def __repr__(self):
        return '#TRANS "{}" {{{}}} "{}" "{}" "{}" "{}" "{}"'.format(
            self.kontonr, ' '.join(self.objekt), self.belopp, self.transdat,
            self.transtext, self.kvantitet, self.sign)

    def __eq__(self, other):
        return all(
            [self.kontonr == other.kontonr, self.objekt == other.objekt,
             self.belopp == other.belopp, self.transdat == other.transdat,
             self.transtext == other.transtext,
             self.kvantitet == other.kvantitet, self.sign == other.sign])

class DataField:
    # pylint: disable=too-few-public-methods
    """Lagrar en post beskriven av en rad"""
    def __init__(self, line):
        self.name = line[0]
        self.data = line[1:]

    def __repr__(self):
        return self.name + ' ' + ' '.join(['"' + x + '"' for x in self.data])

class MaybeDate:
    """Parsar och lagrar ett datum om det finns, annars bara en tom sträng"""
    # pylint: disable=too-few-public-methods
    def __init__(self, datestring):
        try:
            self.date = datetime.strptime(datestring, "%Y%m%d")
            self.year = self.date.year
            self.month = self.date.month
            self.day = self.date.day
            self.has_date = True
        except ValueError:
            self.date = self.year = self.month = None
            self.has_date = False

    def __repr__(self):
        if self.date:
            return self.date.strftime("%Y%m%d")
        else:
            return ''

    def format(self, format_string):
        """Format the date, return an empty string if there is no date"""
        if self.date:
            return self.date.strftime(format_string)
        else:
            return ''

    def __eq__(self, other):
        return self.date.__eq__(other.date)
