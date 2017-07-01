#!/usr/bin/env python3
"""Tests for CSVDict."""

import pytest
from tempfile import NamedTemporaryFile
from csv_dict import CSVDict,CSVKeyMissing

def test_add_items():
    with NamedTemporaryFile(mode='w') as table_file:
        table_file.write("number;a;b\n")
        table_file.flush()
        table = CSVDict(table_file.name)
        table['1'] = {'a': '0', 'b': '2'}

        assert table['1'] == {'a': '0', 'b': '2'}

        table['2'] = {'a': 1, 'b': 2}
        table['3'] = [2, 3]
        table['4'] = '4'

        table2 = CSVDict(table_file.name)

        assert table2['2'] == {'a': '1', 'b': '2'}
        assert table2['3'] == {'a': '2', 'b': '3'}
        assert table2['4']['a'] == '4'

def test_remove_item():
    with NamedTemporaryFile(mode='w') as table_file:
        table_file.write("number;a;b\n")
        table_file.write("1;data;\n")
        table_file.flush()
        table = CSVDict(table_file.name)

        assert table['1']['a'] == 'data'

        del table['1']

        table2 = CSVDict(table_file.name)

        with pytest.raises(CSVKeyMissing):
            _ = table['1']
            _ = table2['1']
