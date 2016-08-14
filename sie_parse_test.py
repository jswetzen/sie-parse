"""Tests for sie parsing"""

import shlex
from tempfile import NamedTemporaryFile
import filecmp

from sie_parse import SieParser
from accounting_data import Transaction

def test_parse_trans():
    """Tests _parse_trans"""
    # pylint: disable=protected-access
    test = ['dummy']
    trans = ['dummy']
    test.append("#TRANS 1 {} 50")
    trans.append(Transaction('1', [], '50'))
    assert SieParser._parse_trans(shlex.split(test[1])) == trans[1]

    test.append("#TRANS 1 {2} 50")
    trans.append(Transaction('1', ['2'], '50'))
    assert SieParser._parse_trans(shlex.split(test[2])) == trans[2]

    test.append("#TRANS 1 {2 3} 50")
    trans.append(Transaction('1', ['2', '3'], '50'))
    assert SieParser._parse_trans(shlex.split(test[3])) == trans[3]

    test.append("#TRANS 2 {} 50 20160806")
    trans.append(Transaction('2', [], '50', '20160806'))
    assert SieParser._parse_trans(shlex.split(test[4])) == trans[4]

    test.append('#TRANS 2 {} 50 20160806 "Transaction 1"')
    trans.append(Transaction('2', [], '50', '20160806', 'Transaction 1'))
    assert SieParser._parse_trans(shlex.split(test[5])) == trans[5]

    test.append('#TRANS 2 {} 50 20160806 "Transaction 1" 2')
    trans.append(Transaction('2', [], '50', '20160806', 'Transaction 1', '2'))
    assert SieParser._parse_trans(shlex.split(test[6])) == trans[6]

    test.append('#TRANS 2 {} 50 20160806 "Transaction 1" 2 "person"')
    trans.append(Transaction('2', [], '50', '20160806', 'Transaction 1', '2', 'person'))
    assert SieParser._parse_trans(shlex.split(test[7])) == trans[7]

    test.append('#TRANS 2 {P-12345} 50')
    trans.append(Transaction('2', ['P-12345'], '50'))
    assert SieParser._parse_trans(shlex.split(test[8])) == trans[8]

    test.append('#TRANS 2 {"10" P-12345} 50')
    trans.append(Transaction('2', ['10', 'P-12345'], '50'))
    assert SieParser._parse_trans(shlex.split(test[9])) == trans[9]

def test_parse_and_write():
    """Parsing the output of write_result should yield the same output"""
    with NamedTemporaryFile() as file1:
        with NamedTemporaryFile() as file2:
            parser = SieParser('testfile.si')
            parser.parse()
            parser.write_result(file1.name)
            parser2 = SieParser(file1.name)
            parser2.parse()
            parser2.write_result(file2.name)
            assert filecmp.cmp(file1.name, file2.name, shallow=False)
