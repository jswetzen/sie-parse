#!/usr/bin/env python3

import sys
import argparse

class SieParser:

    def __init__(self, siefile):
        self.siefile = siefile

    def parse(self):
        if self.siefile:
            with open(self.siefile, 'r', encoding='cp437') as file_handle:
                self._parse_sie(file_handle)
        else:
            self._parse_sie(sys.stdin)

    def _parse_sie(self, handle):
        for line in handle.readlines():
            print(line.strip())


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Parse a .si file')
    argparser.add_argument('--siefile', '-f',
                           help='The file to read, defaults to stdin')
    parser = SieParser('Lön.si')
    parser.parse()
