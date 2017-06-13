#!/usr/bin/python3

import sys
import platform
import ctypes
from pathlib import Path
from itertools import count
import difflib
import PySide
from PySide.QtCore import *
from PySide import QtGui
from PySide.QtGui import *
from sie_parse import SieParser
from petra_output import PetraOutput, CSVKeyMissing

class VismaPetraControls(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.siedata = None
        self.siefilename = None
        self.tabledir = None
        self.account_file = None
        self.costcenter_file = None
        self.project_file = None
        self.initUI()

    def initUI(self):
        # Make the script run as its own program (not as Python) under Windows
        if platform.system() == 'Windows':
            myappid = u'operationmobilisation.petraconverter.1_0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Try to read data tables
        if not self.readTableDir('TABELLER'):
            msg = self.showMessage("Tabellerna hittades inte. Packa upp csv-tabeller till " +
                    str(Path('TABELLER').absolute()),
                    "Tabeller för konto, costcenter och projekt saknas")
            self.close()
            return

        # Create components
        self.sieButton = QtGui.QPushButton("Välj sie-fil")
        self.writeButton = QtGui.QPushButton("Skriv csv")
        self.diffButton = QtGui.QPushButton("Jämför csv")
        self.diffButton.setEnabled(False)
        # Disable buttons if necessary
        if not all((self.account_file, self.costcenter_file, self.project_file)):
            self.sieButton.setEnabled(False)
        if not (self.sieButton.isEnabled() and self.siedata):
            self.writeButton.setEnabled(False)

        # Connect buttons to actions
        self.sieButton.clicked.connect(self.openSIE)
        self.writeButton.clicked.connect(self.writeCSV)
        self.diffButton.clicked.connect(self.diffCSV)

        # Layout elements
        leftbox = QtGui.QVBoxLayout()
        leftbox.addStretch(0)

        rightbox = QtGui.QVBoxLayout()
        rightbox.addStretch(0)

        mainbox = QtGui.QHBoxLayout()
        mainbox.addWidget(self.sieButton)
        mainbox.addWidget(self.writeButton)
        mainbox.addWidget(self.diffButton)
        mainbox.addStretch(0)

        self.setLayout(mainbox)

        self.setGeometry(300, 300, 0, 0)
        self.setWindowTitle("Visma till Petra")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.show()

    def showMessage(self, text, title="Meddelande"):
        msgBox = QMessageBox(self)
        msgBox.setText(text)
        msgBox.setWindowTitle(title)
        msgBox.show()
        return msgBox

    def selectTables(self):
        tabledir = QtGui.QFileDialog.getExistingDirectory(self,
                        "Välj mapp där Costcenter.csv, Konto.csv, och Projekt.csv finns",
                        self.tabledir if self.tabledir else '')
        if tabledir and (not self.readTableDir(tabledir)):
            self.showMessage("Det saknas tabeller i den valda mappen, försök med en annan mapp.")

    def readTableDir(self, directory='.'):
        p = Path(directory)
        tables = list((p / fn for fn in 
                ['Konto.csv', 'Costcenter.csv', 'Projekt.csv']))
        if all(fp.is_file() for fp in tables):
            self.tabledir = directory
            self.account_file = str(tables[0])
            self.costcenter_file = str(tables[1])
            self.project_file = str(tables[2])
            return True
        else:
            return False


    def openSIE(self):
        siefile, _ = QtGui.QFileDialog.getOpenFileName(self, "Öppna sie-fil",
                            '', 'SIE (*.si *.sie);;Alla filer (*.*)')
        if siefile:
            self.siefilename = siefile
            parser = SieParser(siefile)
            parser.parse()
            self.siedata = parser.result
            self.writeButton.setEnabled(True)

    def writeCSV(self):
        siepath = Path(self.siefilename).resolve()
        csvname = siepath.with_suffix('.csv').name
        csvfile = Path('.').resolve() / csvname
        if siepath.parts[-2] == 'SIE':
            csvpath = siepath.parents[1] / 'CSV'
            if csvpath.is_dir():
                csvfile = csvpath / csvname

        self.csvfilename, _ = QtGui.QFileDialog.getSaveFileName(self,
                                "Spara csv som...", str(csvfile))
        retry = True
        while self.csvfilename and retry:
            retry = False
            p_output = PetraOutput(self.siedata, self.account_file,
                    self.costcenter_file, self.project_file)
            try:
                p_output.populate_output_table()
                p_output.write_output(self.csvfilename, True)
                self.showMessage("CSV sparad till " + self.csvfilename)
                self.diffButton.setEnabled(True)
            except CSVKeyMissing as csverr:
                key_info = self.sie_info(csverr.csv_dict.fields[0], csverr.key)
                value, ok = QInputDialog.getText(self, "Ange saknad information",
                        key_info + " saknas. Ange motsvarighet i Petra:\n",
                        QLineEdit.Normal)
                if ok and value:
                    csverr.csv_dict[csverr.key] = value
                    retry = True

    def sie_info(self, field, key):
        """Get info about an account, project or cc with id :key"""
        # TODO: Actually get name or other info, not just print id
        if field == 'V_Kst':
            field_type = 'Costcenter'
        elif field == 'V_Kto':
            field_type = 'Konto'
        elif field == 'V_Proj':
            field_type = 'Projekt'
        return "{} {}".format(field_type, key)

    def diffCSV(self):
        othercsv, _ = QtGui.QFileDialog.getOpenFileName(self, "Välj csv-fil att jämföra med",
                '', 'CSV (*.csv);;Alla filer (*.*)')
        with open(self.csvfilename) as csv1, open(othercsv, encoding='cp1252') as csv2:
            differ = difflib.HtmlDiff()
            csv1_lines = [l.strip() for l in csv1.readlines()
                    if l.strip() and l.strip() != ';;;;;;;']
            csv2_lines = [l.strip() for l in csv2.readlines()
                    if l.strip() and l.strip() != ';;;;;;;']
            diff = differ.make_file(csv1_lines, csv2_lines)
        if diff:
            self.textWidget = QtGui.QTextBrowser()
            self.textWidget.setHtml(diff)
            self.textWidget.resize(700, 500)
            self.textWidget.setWindowTitle("Skillnad mellan program och excel")
            self.textWidget.show()

def main():
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create main window
    window = VismaPetraControls()
    # Enter Qt application main loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
