#!/usr/bin/env python3
"""Läs in en verifikationsfil i .si-format för att kunna exportera till något
annat format"""

import sys
import argparse
import shlex

class SieParser:
    """Parser för ekonomifiler i .si-format"""
    # pylint: disable=too-few-public-methods

    def __init__(self, siefile):
        self.siefile = siefile
        self.has_next = None
        self.parse_result = None
        self.current_line = None
        self.current_object = None
        self.current_list = None

    def parse(self):
        """Läs in filen och tolka den. Returnerar en lista av tolkade objekt"""
        self.has_next = True
        if self.siefile:
            with open(self.siefile, 'r', encoding='cp437') as file_handle:
                result = self._parse_sie(file_handle)
        else:
            result = self._parse_sie(sys.stdin)
        for thing in result:
            print(thing)

    def _parse_sie(self, handle):
        self.parse_result = []
        for self.current_line in handle:
            self._parse_next()
        return self.parse_result

    def _parse_next(self):
        tokens = shlex.split(self.current_line)
        if tokens and tokens[0] == '#VER':
            self.current_object = tokens
        elif tokens and tokens[0] == '{':
            self.current_list = []
        elif tokens and tokens[0] == '}':
            self.parse_result.append((self.current_object, self.current_list))
        elif tokens and tokens[0] == '#TRANS':
            self.current_list.append(tokens)
        elif tokens:
            self.parse_result.append(tokens)
        else:
            pass


if __name__ == "__main__":
    ARGPARSER = argparse.ArgumentParser(
        description='Tolka en verifikationsfil i .si-format')
    ARGPARSER.add_argument('--siefile', '-f',
                           help='The file to read, defaults to stdin')
    PARSER = SieParser('Lön.si')
    PARSER.parse()
