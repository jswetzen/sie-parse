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
        self.last_line = None
        self.last_list = None

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
        while self.has_next:
            parsed = self._parse_next(handle)
            if parsed:
                self.parse_result.append(parsed)
        return self.parse_result

    def _parse_next(self, handle):
        self.last_line = handle.readline()
        if not self.last_line:
            self.has_next = False
            return None
        tokens = shlex.split(self.last_line)
        # print(tokens)
        if tokens and tokens[0] == '#VER':
            # print("Läser verifikation")
            return (tokens, self._parse_next(handle))
        elif tokens and tokens[0] == '{':
            self.last_list = []
            while self.last_line.strip() != '}':
                self.last_list.append(self._parse_next(handle))
            return self.last_list[:-1]
        elif tokens and tokens[0] == '}':
            return None
        elif tokens and tokens[0] == '#TRANS':
            return tokens
        else:
            return None


if __name__ == "__main__":
    ARGPARSER = argparse.ArgumentParser(
        description='Tolka en verifikationsfil i .si-format')
    ARGPARSER.add_argument('--siefile', '-f',
                           help='The file to read, defaults to stdin')
    PARSER = SieParser('Lön.si')
    PARSER.parse()
