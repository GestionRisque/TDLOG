__author__ = 'sihanyou'
# -*- coding: utf-8 -*-
#

# import unittest
import os.path
import sys
import csv
import datetime
import GlobalValue
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import pyqtSignal
from Actif import Actif
import ImportYahooData, SimpleModelling
import logging


# class TestStringMethods(unittest.TestCase):
#     def unitTest(self):
#         self.assertEqual(GlobalValue.ptf[0].nom, 'AAPL')

class Worker(QtCore.QObject):
    precessPercent=pyqtSignal(int)
    def __init__(self):
        super().__init__()
    def preProcess(self, isOnlineMode):
        self.preProcessing(isOnlineMode)
        self.simpleModelling()

    def preProcessing(self,TF):
        if TF:
            logging.debug('{}\tPicking data from local resource...'.format(datetime.datetime.now()))
            readHistData('Historical Data.csv')

        else:
            logging.debug('{}\tPicking data from Yahoo Finance...'.format(datetime.datetime.now()))

            if ImportYahooData.importData() == False:
                logging.debug('{}\tA serieuse warning as above: please check your file!'.format(datetime.datetime.now()))
            else:
                logging.debug('{}\tdata imported successfully from Yahoo!'.format(datetime.datetime.now()))


    def simpleModelling(self):
        logging.debug('{}\tPreparing for the simple modelling...'.format(datetime.datetime.now()))

        try:
            SimpleModelling.main()
        except ValueError:
            logging.debug('{}\tCalculation is wrong somewhere...'.format(datetime.datetime.now()))
            return
        logging.debug('{}\tModelling is successful!'.format(datetime.datetime.now()))
        print(GlobalValue.modelParams)



########## MAIN DIALOG FORM: Main UI ##############

class MainDialog(QtGui.QWidget):
    preProcessRequest=pyqtSignal(bool)

    def __init__(self,worker):
        super(MainDialog, self).__init__()
        self.initUI()
        self.worker=worker
        self.preProcessRequest.connect(self.worker.preProcess)


    def initUI(self):
        self.portfolioText = QtGui.QLabel("Please choose Portfolio Data File Path:", self)
        self.portfolioText.setFont(QtGui.QFont('Times', 20))

        self.processText = QtGui.QLabel("Pre-processing data...", self)
        self.processText.setEnabled(False)

        self.pathEdit = QtGui.QLineEdit(self)
        self.importBtn = QtGui.QPushButton('Import Portfolio Data', self)
        self.importBtn.clicked.connect(self.selectFile)

        self.noInternetBtn = QtGui.QCheckBox('No Internet', self)
        self.noInternetBtn.setEnabled(False)

        self.beginProBtn = QtGui.QPushButton('Begin Pre-processing', self)
        self.beginProBtn.setEnabled(False)
        self.beginProBtn.clicked.connect(self.preProc)

        self.progBar = QtGui.QProgressBar(self)
        self.progBar.setEnabled(False)

        vbox = QtGui.QVBoxLayout();
        hbox1 = QtGui.QHBoxLayout();
        hbox2 = QtGui.QHBoxLayout();
        vbox.addWidget(self.portfolioText)
        hbox1.addWidget(self.pathEdit)
        hbox1.addWidget(self.importBtn)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.processText)
        hbox2.addWidget(self.progBar)
        hbox2.addWidget(self.beginProBtn)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.noInternetBtn)
        self.setLayout(vbox)

        self.setGeometry(300, 100, 500, 300)
        self.setWindowTitle('Portfolio Risk Management Tool')
        self.show()

    def preProc(self):
        self.progBar.setValue(3)
        noInternet=self.noInternetBtn.isChecked()
        self.preProcessRequest.emit(not noInternet)

    def selectFile(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()

        ok=readFile(self.filename)
        if ok:
            self.pathEdit.setText(self.filename)
            self.enableProcessBlock(True)
        else:
            QtGui.QMessageBox.warning(self,"Error","File format is invalid!")

    def enableProcessBlock(self,enable):
        self.progBar.setEnabled(enable)
        self.processText.setEnabled(enable)
        self.noInternetBtn.setEnabled(enable)
        self.processText.setFont(QtGui.QFont('Times', 20))
        self.progressBarValueChange(0)
        self.beginProBtn.setEnabled(True)

    def progressBarValueChange(self, value):
        self.progBar.setValue(value)


########## FROM HERE WE BEGIN TO IMPORT DATA ##############

########## If online, we read only Portfolio Structure ##############
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def readFile(filename):
    ''' stock all actifs infomations in portfolio.'''
    try:
        with open(filename, 'r') as csvfile:
            GlobalValue.ptf = []
            pf = csv.reader(csvfile)
            for row in pf:
                if len(row) != 2 or not is_number(row[1]):
                    return False;
                stockCode=row[0]
                quantity=row[1]
                GlobalValue.ptf.append(Actif(stockCode,quantity))

            csvfile.close()
            logging.debug('{}\tFile imported successfully!'.format(datetime.datetime.now()))
        # print(GlobalValue.ptf[0].stockCode)
        return True;
    except FileNotFoundError:
        logging.debug('{}\tPlease choose the file or close the program!'.format(datetime.datetime.now()))
        sys.exit(app.exec_())


######## If offline, we have to read the historical data values stocked with the name 'Historical Data.csv' ##########

def readHistData(filename):
    # stock all actifs infomations in portfolio.
    try:
        with open(filename, 'r') as csvfile:
            GlobalValue.yahooData = []
            pf = csv.reader(csvfile)
            pf = list(pf)
            temp = []
            for actif in GlobalValue.ptf:
                i = 0
                for column in pf[0]:
                    if column == actif.stockCode:
                        for row in pf:
                            try:
                                temp.append(float(row[i]))
                            except ValueError:
                                print(row[i])
                        break
                    i = i + 1

                GlobalValue.yahooData.append(temp)
                temp = []
            csvfile.close()
            logging.debug('{}\tHistorical Data File imported successfully!'.format(datetime.datetime.now()))

            # print(GlobalValue.ptf[0].nom)

    except FileNotFoundError:
        logging.debug('{}\tPlease choose the file or close the program!'.format(datetime.datetime.now()))
        sys.exit(app.exec_())


########## FROM HERE WE BEGIN THE CALCULATION / MODELLING ##############

########## Pre-Processing will prepare the data we need ##############




if __name__ == '__main__':

    LOG_FILENAME = 'debug.log'
    lognum = 1

    if os.path.isfile('iterate.dat'):
        os.remove('iterate.dat')

    while os.path.isfile(LOG_FILENAME):
        LOG_FILENAME = 'debug' + '(' + str(lognum) + ').log'
        lognum += 1

    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

    logging.debug('******************   Log File  ***********************')

    GlobalValue.init()
    app = QtGui.QApplication(sys.argv)
    worker=Worker()
    workerThread=QtCore.QThread()
    worker.moveToThread(workerThread)
    md = MainDialog(worker)

    sys.exit(app.exec_())
