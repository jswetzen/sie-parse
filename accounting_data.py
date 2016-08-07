"""Klasser för att lagra bokföringsdata från en SI-fil"""

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
        self.serie = serie
        self.vernr = vernr
        self.verdatum = verdatum
        self.vertext = vertext
        self.regdatum = regdatum
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
        return '\n\n'.join(map(str, self.trans_list))
        # return self.trans_list.__repr__()

    def add_trans(self, trans):
        """Lägg till en transaktion till verifikationen"""
        self.trans_list.append(trans)

    def is_complete(self):
        """True om det finns transaktioner inlagda"""
        return bool(self.trans_list)

class Transaction:
    """Lagrar datan för en transaktion"""
    def __init__(self, kontonr, objekt, belopp, transdat='', transtext='',
            kvantitet='', sign=''):
        self.kontonr = kontonr
        self.objekt = objekt
        self.belopp = belopp
        self.transdat = transdat
        self.transtext = transtext
        self.kvantitet = kvantitet
        self.sign = sign

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
    """Lagrar en post beskriven av en rad"""
    def __init__(self, line):
        self.name = line[0]
        self.data = line[1:]

    def __repr__(self):
        return self.name + ' ' + ' '.join(['"' + x + '"' for x in self.data])
