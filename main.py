__author__ = 'sihanyou'
# -*- coding: utf-8 -*-
#

#import unittest
import os.path
import sys
import csv
import datetime
import GlobalValue
from PyQt4.QtGui import *
from Actif import Actif
import ImportYahooData,SimpleModelling
import logging




# class TestStringMethods(unittest.TestCase):
#     def unitTest(self):
#         self.assertEqual(GlobalValue.ptf[0].nom, 'AAPL')


import sys
from PyQt4 import QtGui


class MainDialog(QtGui.QWidget):

    def __init__(self):
        super(MainDialog, self).__init__()

        self.initUI()

    def initUI(self):

        self.text = QtGui.QLabel("Please choose Portfolio Data File Path:",self)
        self.text.setFont(QtGui.QFont('Times',20))
        self.text.move(100,60)
        self.text2 = QtGui.QLabel("Pre-processing data...",self)
        self.text2.resize(500,30)
        self.text2.setVisible(False)
        self.le = QtGui.QLineEdit(self)
        self.le.move(100, 102)
        self.le.resize(500,22)

        self.btn = QtGui.QPushButton('Import Portfolio Data', self)
        self.btn.move(680, 100)
        self.btn.clicked.connect(self.selectFile)

        self.btn3 = QtGui.QCheckBox('No Internet',self)
        self.btn3.move(680, 200)
        self.btn3.setVisible(False)

        self.btn2 = QtGui.QPushButton('Begin Pre-processing', self)
        self.btn2.setVisible(False)
        self.btn2.move(680, 160)
        self.btn2.clicked.connect(self.preProc)

        self.prg = QtGui.QProgressBar(self)
        self.prg.setVisible(False)

        self.setGeometry(300, 100, 1000, 500)
        self.setWindowTitle('Portfolio Risk Management Tool')
        self.show()

    def preProc(self):
        self.prg.setValue(3)

        if self.btn3.isChecked():
            preProcessing(True)
            simpleModelling(1)
        else:
            preProcessing(False)
            simpleModelling(2)

    def selectFile(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()
        self.le.setText(self.filename)
        self.prg.setVisible(True)
        self.text2.setVisible(True)
        self.btn3.setVisible(True)
        self.text2.setFont(QtGui.QFont('Times',20))
        self.text2.move(100,160)
        self.prg.move(100,200)
        self.prg.resize(500,30)
        self.prg.setValue(0)
        readFile(self.filename)
        self.btn2.setVisible(True)


########## from here we begin to import data ##############



def readFile(filename):
    # stock all actifs infomations in portfolio.
    try:
        with open(filename, 'r') as csvfile:
            GlobalValue.ptf = []
            pf = csv.reader(csvfile)
            for row in pf:
                GlobalValue.ptf.append(Actif(row))

            csvfile.close()
            logging.debug('{}           File imported successfully!'.format(datetime.datetime.now()))

            #print(GlobalValue.ptf[0].nom)

    except FileNotFoundError:
        logging.debug('{}           Please choose the file or close the program!'.format(datetime.datetime.now()))
        sys.exit(app.exec_())




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
                    if column==actif.nom:
                        for row in pf:
                            try:
                                temp.append(float(row[i]))
                            except ValueError:
                                print(row[i])
                        break
                    i=i+1

                GlobalValue.yahooData.append(temp)
                temp = []
            csvfile.close()
            logging.debug('{}           Historical Data File imported successfully!'.format(datetime.datetime.now()))

            #print(GlobalValue.ptf[0].nom)

    except FileNotFoundError:
        logging.debug('{}           Please choose the file or close the program!'.format(datetime.datetime.now()))
        sys.exit(app.exec_())


########## from here we begin the calculation ##############


def preProcessing(TF):

    if TF:
        readHistData('Historical Data.csv')

    else:
        logging.debug('{}           Picking data from Yahoo Finance...'.format(datetime.datetime.now()))

        if ImportYahooData.main() == 0:
            logging.debug('{}           A serieuse warning as above: please check your file!'.format(datetime.datetime.now()))
        else:
            logging.debug('{}           data imported successfully from Yahoo!'.format(datetime.datetime.now()))

def simpleModelling(i):

    logging.debug('{}           Preparing for the simple modelling...'.format(datetime.datetime.now()))

    try:
        SimpleModelling.main(i)
    except ValueError:
        logging.debug('{}           Calculation is wrong somewhere...'.format(datetime.datetime.now()))
        return
    logging.debug('{}           Modelling is successful!'.format(datetime.datetime.now()))
    print(GlobalValue.modelParams)






if __name__ == '__main__':

    LOG_FILENAME = 'debug.log'
    lognum = 1

    if os.path.isfile('iterate.dat'):
        os.remove('iterate.dat')

    while os.path.isfile(LOG_FILENAME):
        LOG_FILENAME = 'debug'+ '(' +str(lognum)+ ').log'
        lognum += 1

    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

    logging.debug('******************   Log File  ***********************')

    GlobalValue.init()
    app = QtGui.QApplication(sys.argv)

    md = MainDialog()

    sys.exit(app.exec_())