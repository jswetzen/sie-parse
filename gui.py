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
from accounting_data import SieIO
from petra_output import PetraOutput
from csv_dict import CSVKeyMissing
from visma_output import PetraParser
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)


class VismaPetraControls(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.siedata = None
        self.siefile = None
        self.petrafile = None
        self.petra_parser = None
        self.tabledir = None
        self.kto_acct_file = None
        self.re_cc_file = None
        self.proj_cc_file = None
        self.acct_kto_file = None
        self.cc_re_proj_file = None
        self.sie_defaults_file = None
        self.sie_dims_file = None
        self.sie_units_file = None
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
        self.readSieButton = QtGui.QPushButton("Välj SI-fil")
        self.writePetraButton = QtGui.QPushButton("Skriv petra-fil")
        self.diffButton = QtGui.QPushButton("Jämför csv")
        self.readPetraButton = QtGui.QPushButton("Välj petra-fil")
        self.writeVismaButton = QtGui.QPushButton("Skriv SI-fil")

        # Disable buttons if necessary
        self.diffButton.setEnabled(False)
        self.writeVismaButton.setEnabled(False)
        if not all((self.kto_acct_file, self.re_cc_file, self.proj_cc_file)):
            self.readSieButton.setEnabled(False)
        if not (self.readSieButton.isEnabled() and self.siedata):
            self.writePetraButton.setEnabled(False)

        # Connect buttons to actions
        self.readSieButton.clicked.connect(self.openSIE)
        self.writePetraButton.clicked.connect(self.writeCSV)
        self.diffButton.clicked.connect(self.diffCSV)
        self.readPetraButton.clicked.connect(self.openPetraCSV)
        self.writeVismaButton.clicked.connect(self.writeSIE)

        # Layout elements
        vismaPetraBox = QtGui.QHBoxLayout()
        vismaPetraBox.addWidget(self.readSieButton)
        vismaPetraBox.addWidget(QtGui.QLabel("=>"))
        vismaPetraBox.addWidget(self.writePetraButton)
        vismaPetraBox.addWidget(QtGui.QLabel("=>"))
        vismaPetraBox.addWidget(self.diffButton)
        vismaPetraBox.addStretch(0)

        petraVismaBox = QtGui.QHBoxLayout()
        petraVismaBox.addWidget(self.readPetraButton)
        petraVismaBox.addWidget(QtGui.QLabel("=>"))
        petraVismaBox.addWidget(self.writeVismaButton)
        petraVismaBox.addStretch(0)

        mainBox = QtGui.QVBoxLayout()
        mainBox.addWidget(QtGui.QLabel("Visma till Petra"))
        mainBox.addLayout(vismaPetraBox)
        mainBox.addWidget(QtGui.QLabel("Petra till Visma"))
        mainBox.addLayout(petraVismaBox)
        mainBox.addStretch(0)

        self.setLayout(mainBox)

        self.setGeometry(300, 300, 0, 0)
        self.setWindowTitle("Konverterare mellan Petra och Visma")
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
                        "Välj mapp där Kto_Acct.csv, Re_CC.csv, och Proj_CC.csv finns",
                        self.tabledir if self.tabledir else '')
        if tabledir and (not self.readTableDir(tabledir)):
            self.showMessage("Det saknas tabeller i den valda mappen, försök med en annan mapp.")

    def readTableDir(self, directory='.'):
        p = Path(directory)
        tables = list((p / fn for fn in ['Kto_Acct.csv', 'Re_CC.csv',
            'Proj_CC.csv', 'Acct_Kto.csv', 'CC_Re_Proj.csv',
            'SIE_defaults.csv', 'SIE_dims.csv', 'SIE_units.csv']))
        if all(fp.is_file() for fp in tables):
            self.tabledir = directory
            self.kto_acct_file = str(tables[0])
            self.re_cc_file = str(tables[1])
            self.proj_cc_file = str(tables[2])
            self.acct_kto_file = str(tables[3])
            self.cc_re_proj_file = str(tables[4])
            self.sie_defaults_file = str(tables[5])
            self.sie_dims_file = str(tables[6])
            self.sie_units_file = str(tables[7])
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
            self.writePetraButton.setEnabled(True)

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
            p_output = PetraOutput(self.siedata, self.kto_acct_file,
                    self.re_cc_file, self.proj_cc_file)
            try:
                p_output.populate_output_table()
                p_output.write_output(self.csvfilename, True)
                self.showMessage("CSV sparad till " + self.csvfilename)
                self.diffButton.setEnabled(True)
                retry = False
            except CSVKeyMissing as csverr:
                retry = self.complement_csv(csverr)

    def complement_csv(self, csverr):
        """
        Given a CSVKeyMissing exception, prompt the user to add missing data.
        """
        values, ok = QMultiInputDialog.getInputs(title='Ange saknad information',
            text=self.sie_info(csverr),
            fields=csverr.csv_dict.fields,
            values={csverr.csv_dict.fields[0]: csverr.key})
        if ok and values:
            csverr.csv_dict[csverr.key] = values
            return True
        else:
            return False

    def sie_info(self, csverr):
        """Get info about an account, project or cc with id :key"""
        csvfile = csverr.csv_dict.csv_filename
        key = csverr.key
        field = csverr.csv_dict.fields[0]
        program = "Visma" if field[0] == 'P' else "Petra"
        return "Index {} saknas i {}. Ange motsvarighet i {}.".format(
                key, csvfile, program)

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

    def openPetraCSV(self):
        self.petrafile, _ = QtGui.QFileDialog.getOpenFileName(self, "Öppna petra-fil",
                '', 'CSV (*.csv *.txt);;Alla filer (*.*)')
        if self.petrafile:
            self.petra_parser = PetraParser(
                    self.petrafile, self.acct_kto_file, cc_re_proj_file,
                    sie_defaults_file, sie_dims_file, sie_units_file,
                    kto_acct_file, re_cc_file, proj_cc_file)
            self.writeVismaButton.setEnabled(True)

    def writeSIE(self):
        csvpath = Path(self.petrafile).resolve()
        siename = csvpath.with_suffix('.SI').name
        siefile = Path('.').resolve() / siename

        siefilename, _ = QtGui.QFileDialog.getSaveFileName(self,
                                "Spara SI som...", str(siefile))
        retry = True
        while siefilename and retry:
            try:
                self.petra_parser.make_sie_data()
                if not self.petra_parser.sie_data.is_complete():
                    self.showMessage("Något saknas i SIE-filen")
                else:
                    SieIO.writeSie(self.petra_parser.sie_data, siefilename, True)
                    self.showMessage("SI sparad till " + siefilename)
                retry = False
            except CSVKeyMissing as csverr:
                retry = self.complement_csv(csverr)


class QMultiInputDialog(QDialog):
    """Get several inputs in one dialog."""
    def __init__(self, parent=None, title=None, text=None, fields=[''], values={}, f=0):
        """Show text and get input for every name in the list fields."""
        super().__init__(parent, f)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(text))

        inputGrid = QGridLayout()
        layout.addLayout(inputGrid)

        self.inputs = {f: QLineEdit(self) for f in fields}

        for idx, field in enumerate(fields):
            if field in values:
                self.inputs[field].setText(values[field])
                self.inputs[field].setEnabled(False)
            inputGrid.addWidget(QLabel(field), idx, 0)
            inputGrid.addWidget(self.inputs[field], idx, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def getValues(self):
        """Get current values from the text input fields"""
        return {key: line.text() for key, line in self.inputs.items()}

    @staticmethod
    def getInputs(parent=None, title=None, text=None, fields=[], values={}, f=0):
        dialog = QMultiInputDialog(parent, title, text, fields, values, f)
        result = dialog.exec_()
        values = dialog.getValues()
        return (values, result == QDialog.Accepted)

def main():
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create main window
    window = VismaPetraControls()
    # Enter Qt application main loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
