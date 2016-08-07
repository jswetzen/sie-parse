"""Tests for sie parsing"""

import shlex

from sie_parse import SieParser
from accounting_data import Transaction

class TestSieParse:
    """Tests for SieParser"""
    def test_parse_trans(self):
        test1 = "#TRANS 1 {} 50"
        trans1 = Transaction('1', [], '50')
        assert SieParser._parse_trans(shlex.split(test1)) == trans1

        test2 = "#TRANS 1 {2} 50"
        trans2 = Transaction('1', ['2'], '50')
        assert SieParser._parse_trans(shlex.split(test2)) == trans2

        test3 = "#TRANS 1 {2 3} 50"
        trans3 = Transaction('1', ['2', '3'], '50')
        assert SieParser._parse_trans(shlex.split(test3)) == trans3

        test4 = "#TRANS 2 {} 50 20160806"
        trans4 = Transaction('2', [], '50', '20160806')
        assert SieParser._parse_trans(shlex.split(test4)) == trans4

        test5 = '#TRANS 2 {} 50 20160806 "Transaction 1"'
        trans5 = Transaction('2', [], '50', '20160806', 'Transaction 1')
        assert SieParser._parse_trans(shlex.split(test5)) == trans5

        test6 = '#TRANS 2 {} 50 20160806 "Transaction 1" 2'
        trans6 = Transaction('2', [], '50', '20160806', 'Transaction 1', '2')
        assert SieParser._parse_trans(shlex.split(test6)) == trans6

        test7 = '#TRANS 2 {} 50 20160806 "Transaction 1" 2 "person"'
        trans7 = Transaction('2', [], '50', '20160806', 'Transaction 1', '2', 'person')
        assert SieParser._parse_trans(shlex.split(test7)) == trans7

        test8 = '#TRANS 2 {P-12345} 50'
        trans8 = Transaction('2', ['P-12345'], '50')
        assert SieParser._parse_trans(shlex.split(test8)) == trans8

        test9 = '#TRANS 2 {"10" P-12345} 50'
        trans9 = Transaction('2', ['10', 'P-12345'], '50')
        assert SieParser._parse_trans(shlex.split(test9)) == trans9
