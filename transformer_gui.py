#!/usr/bin/python3

import sys
from pathlib import Path
from itertools import count
import difflib
from PySide.QtCore import *
from PySide import QtGui
from PySide.QtGui import *
from sie_parse import SieParser
from petra_output import PetraOutput

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
        # Create components
        tableButton = QtGui.QPushButton("Välj tabellmapp")
        self.sieButton = QtGui.QPushButton("Välj sie-fil")
        self.writeButton = QtGui.QPushButton("Skriv csv")
        self.diffButton = QtGui.QPushButton("Jämför csv")
        self.diffButton.setEnabled(False)
        # Disable buttons if necessary
        if not all((self.account_file, self.costcenter_file, self.project_file)):
            self.sieButton.setEnabled(False)
        if not (self.sieButton.isEnabled() and self.siedata):
            self.writeButton.setEnabled(False)
        # Try a default path for tables
        self.readTableDir('TABELLER')

        # Connect buttons to actions
        tableButton.clicked.connect(self.selectTables)
        self.sieButton.clicked.connect(self.openSIE)
        self.writeButton.clicked.connect(self.writeCSV)
        self.diffButton.clicked.connect(self.diffCSV)

        # Layout elements
        leftbox = QtGui.QVBoxLayout()
        leftbox.addWidget(tableButton)
        leftbox.addWidget(self.sieButton)
        leftbox.addStretch(0)

        rightbox = QtGui.QVBoxLayout()
        rightbox.addWidget(self.writeButton)
        rightbox.addWidget(self.diffButton)
        rightbox.addStretch(0)

        mainbox = QtGui.QHBoxLayout()
        mainbox.addLayout(leftbox)
        mainbox.addLayout(rightbox)
        mainbox.addStretch(0)

        self.setLayout(mainbox)

    def showMessage(self, text):
        msgBox = QMessageBox(self)
        msgBox.setText(text)
        msgBox.show()

    def selectTables(self):
        tabledir = QtGui.QFileDialog.getExistingDirectory(self,
                        "Välj mapp där Costcenter.csv, Konto.csv, och Projekt.csv finns",
                        self.tabledir if self.tabledir else '')
        if tabledir and (not self.readTableDir(tabledir)):
            self.showMessage("Det saknas tabeller i den valda mappen, försök med en annan mapp.")

    def readTableDir(self, directory='.'):
        p = Path(directory)
        account, costcenter, project = (p / fn for fn in 
                ['Konto.csv', 'Costcenter.csv', 'Projekt.csv'])
        if all(fp.is_file() for fp in [account, costcenter, project]):
            self.tabledir = directory
            self.account_file = str(account)
            self.costcenter_file = str(costcenter)
            self.project_file = str(project)
            self.sieButton.setEnabled(True)
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
        if self.csvfilename:
            p_output = PetraOutput(self.siedata, self.account_file,
                    self.costcenter_file, self.project_file)
            p_output.populate_output_table()
            p_output.write_output(self.csvfilename, True)
            self.showMessage("CSV sparad till " + self.csvfilename)
            self.diffButton.setEnabled(True)

    def diffCSV(self):
        othercsv, _ = QtGui.QFileDialog.getOpenFileName(self, "Välj csv-fil att jämföra med",
                '', 'CSV (*.csv);;Alla filer (*.*)')
        with open(self.csvfilename) as csv1, open(othercsv, encoding='cp1252') as csv2:
            differ = difflib.HtmlDiff()
            csv1_lines = [l.strip() for l in csv1.readlines()
                    if l.strip() and l.strip() != ';;;;;;;']
            csv2_lines = [l.strip() for l in csv2.readlines()
                    if l.strip() and l.strip() != ';;;;;;;']
            # diff = list(differ.compare(csv1_lines, csv2_lines))
            diff = differ.make_file(csv1_lines, csv2_lines)
        if diff:
            # diffmessage = ("\n".join(diff))
            # self.textWidget = QtGui.QPlainTextEdit("\n".join(diff))
            self.textWidget = QtGui.QTextBrowser()
            self.textWidget.setHtml(diff)
            self.textWidget.resize(700, 500)
            self.textWidget.setWindowTitle("Skillnad mellan program och excel")
            # self.textWidget.setFont(QFont("Courier New"))
            self.textWidget.show()

class VismaPetraWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        controls = VismaPetraControls()
        self.setCentralWidget(controls)

        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        # openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("Visma till Petra")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.show()
        msgBox = QMessageBox()
        msgBox.setText("Hello World - using PySide version " + PySide.__version__)
        # msgBox.show()

def main():
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create main window
    window = VismaPetraWindow()
    # Enter Qt application main loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
