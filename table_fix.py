#!/usr/bin/env python3
from csv_dict import CSVDict, CSVKeyMissing
from sie_parse import SieParser
import tools

re_cc = CSVDict('TABELLER/Re_CC.csv')
costcenter = CSVDict('TABELLER_old/Costcenter.csv')
kto_acct = CSVDict('TABELLER/Kto_Acct.csv')
konto = CSVDict('TABELLER_old/Konto.csv')
proj_cc = CSVDict('TABELLER/Proj_CC.csv')
projekt = CSVDict('TABELLER_old/Projekt.csv')

for k,v in projekt.items():
    if k not in proj_cc:
        proj_cc[k] = ['', v['P_Kst_P']]

for k,v in konto.items():
    if k not in kto_acct:
        kto_acct[k] = {'P_Acct': v['P_Kto']}

for k,v in costcenter.items():
    if k not in re_cc:
        re_cc[k] = {'P_CC': v['P_Kst']}

parser = SieParser('SIE/VtP_201710_1.si')
parser.parse()

tools.add_accounts_from_sie(parser.result, 'TABELLER/Kto_Acct.csv')
tools.add_objects_from_sie(parser.result, 'TABELLER/SIE_objects_1.csv', 'TABELLER/SIE_objects_6.csv')
tools.complement_from_SIE('TABELLER/SIE_objects_1.csv', 'TABELLER/Re_CC.csv')
tools.complement_from_SIE('TABELLER/SIE_objects_6.csv', 'TABELLER/Proj_CC.csv')

print(len([v for v in re_cc.values() if v['Name'] == '']))
print(len([v for v in proj_cc.values() if v['Name'] == '']))
print(len([v for v in kto_acct.values() if v['KONTO'] == '']))
