__author__ = 'sihanyou'
# -*- coding: utf-8 -*-
#

# import unittest
import os.path
import sys
import csv
import datetime
import GlobalValue
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import pyqtSignal
from Actif import Actif
import ImportYahooData, SimpleModelling
import logging
import plot
import pickle
import Aggregation

# class TestStringMethods(unittest.TestCase):
#     def unitTest(self):
#         self.assertEqual(GlobalValue.ptf[0].nom, 'AAPL')
def debugOutput(message):
    print("log: " + message)
    logging.debug(('{}\t' + message).format(datetime.datetime.now()))


class Worker(QtCore.QObject):
    processPercent = pyqtSignal(int)
    simpleModelSucceed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def preProcess(self, isOffLine, isDebugMode):
        print("preProcess")
        self.preProcessing(isOffLine, isDebugMode)
        currentPercent = 10
        self.processPercent.emit(currentPercent)
        self.simpleModelling(currentPercent)
        self.processPercent.emit(100)

    def preProcessing(self, noInternet, debugMode):
        if noInternet:
            debugOutput('Picking data from local resource...')
            if debugMode:
                readHistData('Historical Data Short.csv')
            else:
                readHistData('Historical Data.csv')

        else:
            debugOutput('Picking data from Yahoo Finance...')
            if ImportYahooData.importData() == False:
                debugOutput('A serieuse warning as above: please check your file!')
            else:
                debugOutput('data imported successfully from Yahoo!')

    def simpleModelling(self, currentPercent):
        debugOutput("Preparing for the simple modelling..")

        try:
            SimpleModelling.main(self.processPercent, currentPercent)
        except ValueError:
            debugOutput("Calculation is wrong somewhere")
            self.simpleModelSucceed.emit(False)
            return
        debugOutput("Modeling is successful!")
        print(GlobalValue.modelParams)

        self.simpleModelSucceed.emit(True)


########## MAIN DIALOG FORM: Main UI ##############
class ModelChoiceDialog(QtGui.QDialog):
    def __init__(self, portfolio, parent):
        super(ModelChoiceDialog, self).__init__(parent)
        self.actifCount = len(portfolio)
        self.armaCheck = list()
        self.garchCheck = list()
        self.svCheck = list()
        self.vBox = QtGui.QVBoxLayout()

        for i in range(self.actifCount):
            self.armaCheck.append(QtGui.QRadioButton('ARMA', self))
            self.garchCheck.append(QtGui.QRadioButton('GARCH', self))
            self.svCheck.append(QtGui.QRadioButton('SV', self))
            userChoiceGroupBox = QtGui.QGroupBox('Please select one model for the stock ' + portfolio[i].stockCode, self)
            radioVBox = QtGui.QVBoxLayout()
            radioVBox.addWidget(self.armaCheck[i])
            radioVBox.addWidget(self.garchCheck[i])
            radioVBox.addWidget(self.svCheck[i])
            userChoiceGroupBox.setLayout(radioVBox)
            self.vBox.addWidget(userChoiceGroupBox)
        self.setLayout(self.vBox)

    def getResult(self):
        result = list()
        for i in range(self.actifCount):
            if self.armaCheck[i].isChecked():
                result.append(0)
            elif self.garchCheck[i].isChecked():
                result.append(1)
            elif self.svCheck[i].isChecked():
                result.append(2)
            else:
                result.append(-1)
        return result


class MainDialog(QtGui.QWidget):
    preProcessRequest = pyqtSignal(bool, bool)

    def __init__(self):
        super(MainDialog, self).__init__()
        self.initUI()

    def setWorker(self, worker):
        self.worker = worker
        self.preProcessRequest.connect(self.worker.preProcess)
        worker.processPercent.connect(self.progressBarValueChange)
        worker.simpleModelSucceed.connect(self.simpleModellingFinishReceiver)

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

        self.debugTestBtn = QtGui.QCheckBox('Debug Mode(fewer data, faster processing)', self)
        self.debugTestBtn.setEnabled(False)

        self.beginProBtn = QtGui.QPushButton('Begin Pre-processing', self)
        self.beginProBtn.clicked.connect(self.preProc)

        self.progBar = QtGui.QProgressBar(self)

        self.modelChoiceBtn = QtGui.QPushButton('Choose Models for stocks', self)
        self.modelChoiceBtn.clicked.connect(self.chooseModel)

        self.modelInfoLabel = QtGui.QLabel(self)
        self.updateModelLabel()
        self.modelGroupeBox = QtGui.QGroupBox('Chosen Model:', self)
        modelLayout = QtGui.QVBoxLayout()
        modelLayout.addWidget(self.modelInfoLabel)
        self.modelGroupeBox.setLayout(modelLayout)

        self.beginSimulationBtn = QtGui.QPushButton('Begin simulation', self)
        self.beginSimulationBtn.clicked.connect(self.beginSimulation)

        mainVBox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        mainVBox.addWidget(self.portfolioText)
        hbox1.addWidget(self.pathEdit)
        hbox1.addWidget(self.importBtn)
        mainVBox.addLayout(hbox1)
        mainVBox.addWidget(self.processText)
        hbox2.addWidget(self.progBar)
        hbox2.addWidget(self.beginProBtn)
        mainVBox.addLayout(hbox2)
        mainVBox.addWidget(self.noInternetBtn)
        mainVBox.addWidget(self.debugTestBtn)
        mainVBox.addWidget(self.modelChoiceBtn)
        mainVBox.addWidget(self.modelGroupeBox)
        mainVBox.addWidget(self.beginSimulationBtn)
        self.setLayout(mainVBox)

        self.setGeometry(300, 100, 500, 300)
        self.setWindowTitle('Portfolio Risk Management Tool')
        self.show()

        self.enableProcessBlock(False)
        self.enableSimulationBlock(False)

    def updateModelLabel(self):
        s = ''
        if len(GlobalValue.ptf) == 0:
            s = 'No stock name found.'
        elif len(GlobalValue.modelChoice) == 0:
            for i in range(len(GlobalValue.ptf)):
                actifName = GlobalValue.ptf[i].stockCode
                s = s + actifName + ': no model chosen\n'
        else:
            assert len(GlobalValue.modelChoice) == len(GlobalValue.ptf)
            for i in range(len(GlobalValue.ptf)):
                actifName = GlobalValue.ptf[i].stockCode
                s = s + actifName + ': '
                if GlobalValue.modelChoice[i] == 0:
                    s = s + 'arma\n'
                elif GlobalValue.modelChoice[i] == 1:
                    s = s + 'garch\n'
                elif GlobalValue.modelChoice[i] == 2:
                    s = s + 'sv\n'
                else:
                    s = s + 'no model chosen\n'
        self.modelInfoLabel.setText(s)

    def preProc(self):
        self.progBar.setValue(3)
        noInternet = self.noInternetBtn.isChecked()
        debugMode = self.debugTestBtn.isChecked()
        self.preProcessRequest.emit(noInternet, debugMode)

    def selectFile(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()

        ok = readFile(self.filename)
        if ok:
            self.pathEdit.setText(self.filename)
            self.enableProcessBlock(True)
        else:
            QtGui.QMessageBox.warning(self, "Error", "File format is invalid!")

    def chooseModel(self):
        modelDialog = ModelChoiceDialog(GlobalValue.ptf, self)
        modelDialog.setGeometry(300, 100, 500, 300)
        modelDialog.setWindowTitle('Choose model')
        modelDialog.exec_()
        GlobalValue.modelChoice = modelDialog.getResult()
        self.updateModelLabel()

    def beginSimulation(self):
        self.applyModel()
        Aggregation.agregation()

    def simpleModellingFinishReceiver(self, succeed):
        if succeed:
            self.enableSimulationBlock(True)
            pickle.dump(GlobalValue.modelParams, open("globalValue_modelParams.dat", "wb"))
            pickle.dump(GlobalValue.yahooData, open("globalValue_yahooData.dat", "wb"))
        else:
            self.enableSimulationBlock(False)
            QtGui.QMessageBox.warning(self, "Error", "Simple Modelling failed!")
        for i in range(len(GlobalValue.yahooData)):
            plot.plot_simulation(GlobalValue.modelParams[i], GlobalValue.yahooData[i],i)

    def enableProcessBlock(self, enable):
        self.progBar.setEnabled(enable)
        self.processText.setEnabled(enable)
        self.noInternetBtn.setEnabled(enable)
        self.debugTestBtn.setEnabled(enable)
        self.processText.setFont(QtGui.QFont('Times', 20))
        self.progressBarValueChange(0)
        self.beginProBtn.setEnabled(True)

    def enableSimulationBlock(self, enable):
        self.beginSimulationBtn.setEnabled(enable)

    def progressBarValueChange(self, value):
        self.progBar.setValue(value)

    def applyModel(self):
        # TODO: change assert to if to give a warning dialog
        assert len(GlobalValue.ptf) == len(GlobalValue.modelParams)
        assert len(GlobalValue.ptf) == len(GlobalValue.modelChoice)
        assert len(GlobalValue.ptf) == len(GlobalValue.yahooData)
        assert len(GlobalValue.ptf) > 0
        for i in range(len(GlobalValue.ptf)):
            assert GlobalValue.modelChoice[i] >= 0
            assert GlobalValue.modelChoice[i] <= 2

        GlobalValue.simulations = []
        for i in range(len(GlobalValue.ptf)):
            if GlobalValue.modelChoice[i] == 0:
                returns = SimpleModelling.returns(GlobalValue.yahooData[i])
                GlobalValue.simulations.append(plot.choice_ARMA(GlobalValue.modelParams[i]['arma'], returns))
            elif GlobalValue.modelChoice[i] == 1:
                GlobalValue.simulations.append(plot.Plot_GARCH(GlobalValue.modelParams[i]['garch']))
            elif GlobalValue.modelChoice[i] == 2:
                GlobalValue.simulations.append(plot.Plot_SV(GlobalValue.modelParams[i]['sv']))
            else:
                assert False

        print(GlobalValue.simulations[0])


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
                    return False
                stockCode = row[0]
                quantity = row[1]
                GlobalValue.ptf.append(Actif(stockCode, quantity))

            csvfile.close()
            debugOutput("File imported successfully!")
        # print(GlobalValue.ptf[0].stockCode)
        return True
    except FileNotFoundError:
        debugOutput("Please choose the file or close the program!")
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
            debugOutput("Historical Data File imported successfully!")

            # print(GlobalValue.ptf[0].nom)

    except FileNotFoundError:
        debugOutput("Please choose the file or close the program!")
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
    worker = Worker()
    workerThread = QtCore.QThread()
    worker.moveToThread(workerThread)
    md = MainDialog()
    md.setWorker(worker)
    workerThread.start()

    sys.exit(app.exec_())
