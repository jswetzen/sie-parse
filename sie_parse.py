#!/usr/bin/env python3
"""Läs in en verifikationsfil i .si-format för att kunna exportera till något
annat format"""

import sys
import argparse
import shlex

from accounting_data import SieData, Verification, Transaction, DataField
from petra_output import PetraOutput

class SieParser:
    """Parser för ekonomifiler i .si-format"""
    # pylint: disable=too-few-public-methods

    def __init__(self, siefile):
        self.siefile = siefile
        self.has_next = None
        self.parse_result = None
        self.current_line = None
        self.current_verification = None
        self.result = None

    def parse(self):
        """Läs in filen och tolka den. Returnerar en lista av tolkade objekt"""
        self.has_next = True
        if self.siefile:
            with open(self.siefile, 'r', encoding='cp437') as file_handle:
                self.result = self._parse_sie(file_handle)
        else:
            self.result = self._parse_sie(sys.stdin)

    def write_result(self, filename):
        """Skriv resultatet till en fil, med rätt teckenkodning"""
        if self.result:
            with open(filename, 'w', encoding='cp437') as file_handle:
                file_handle.write(repr(self.result))
        else:
            print("write_result: nothing to write")

    def _parse_sie(self, handle):
        self.parse_result = SieData()
        for self.current_line in handle:
            self._parse_next()
        return self.parse_result

    def _parse_next(self):
        tokens = shlex.split(self.current_line)
        if tokens and tokens[0] == '#VER':
            self.current_verification = Verification(*tokens[1:])
        elif tokens and tokens[0] == '{':
            pass
        elif tokens and tokens[0] == '}':
            self.parse_result.add_data('#VER', self.current_verification)
        elif tokens and tokens[0] == '#TRANS':
            self.current_verification.add_trans(self._parse_trans(tokens))
        elif tokens:
            self.parse_result.add_data(tokens[0], DataField(tokens))
        else:
            pass

    @staticmethod
    def _parse_trans(tokens):
        args = tokens[1:2]

        if tokens[2] == '{}':
            args = args + [[]] + tokens[3:]
        else:
            if tokens[2].endswith('}'):
                objekt = [tokens[2][1:-1]]
                args = args + [objekt] + tokens[3:]
            else:
                objekt = [tokens[2][1:]]
                for idx, token in enumerate(tokens[3:]):
                    if token.endswith('}'):
                        objekt.append(token[:-1])
                        args = args + [objekt] + tokens[4+idx:]
                        break
                    else:
                        objekt.append(token)
        return Transaction(*args)

if __name__ == "__main__":
    ARGPARSER = argparse.ArgumentParser(
        description='Tolka en verifikationsfil i .si-format')
    ARGPARSER.add_argument('siefile', metavar='siefile',
                           help='The file to read, defaults to stdin')
    ARGS = ARGPARSER.parse_args()
    FILENAME = '.'.join(ARGS.siefile.split('/')[-1].split('.')[:-1])
    PARSER = SieParser(ARGS.siefile)
    PARSER.parse()
    # print(PARSER.result)
    P_OUTPUT = PetraOutput(PARSER.result, 'TABELLER/Konto.csv',
            'TABELLER/Costcenter.csv', 'TABELLER/Projekt.csv')
    P_OUTPUT.populate_output_table()
    # P_OUTPUT.print_output()
    P_OUTPUT.write_output('CSV/' + FILENAME + '.csv')
