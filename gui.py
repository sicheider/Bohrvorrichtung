import sys
import json
import logging
import communicationUtilities
import commands
import os
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot

class Gui(QtGui.QDialog):

    receivedResponse = pyqtSignal(str)

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Interface.ui")

        self.loadAllProcessData()

        logging.basicConfig(level = logging.DEBUG)

        self.cs = communicationUtilities.CommandSender(self)
        self.cs.start()
        self.allowedToSend = True

        self.receivedResponse.connect(self.onReceiveResponseEvent)

        #setup combobox
        for processData in self.allProcessData:
            self.ui.comboBox.addItem(processData["name"])
        self.onComboBoxChanged()

        #connect events
        self.ui.comboBox.currentIndexChanged.connect(self.onComboBoxChanged)
        self.ui.saveDataButton.clicked.connect(self.onSaveButtonClicked)
        self.ui.saveDataAndLoadButton.clicked.connect(self.onSaveDataAndLoadButtonClicked)
        self.ui.deleteDataButton.clicked.connect(self.onDeleteButtonClicked)
        self.ui.driveX1Button.clicked.connect(self.onDriveToX1ButtonClicked)
        self.ui.driveX2Button.clicked.connect(self.onDriveToX2ButtonClicked)
        self.ui.driveX3Button.clicked.connect(self.onDriveToX3ButtonClicked)
        self.ui.startButton.clicked.connect(self.onStartButtonClicked)
        self.ui.stopButton.clicked.connect(self.onStopButtonClicked)

        self.ui.show()

    def loadAllProcessData(self):
        data = open("allProcessData.json", "r")
        self.allProcessData = json.loads(data.read())
        logging.info("Loaded all process data:")
        logging.info(str(self.allProcessData))
        data.close()

    @pyqtSlot(str)
    def onReceiveResponseEvent(self, response):
        logging.info(response)
        if response == commands.INTERRUPT:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Bohrvorrichtung wurde gestoppt!")
        if response == commands.RESPONSE_FAIL:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Operation fehlgeschlagen!")
        if response == commands.INVALID_REQUEST:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Ungueltige Anforderung!")
        self.enableWidgets()

    def onResponse(self, response):
        self.receivedResponse.emit(response)

    def onSaveDataAndLoadButtonClicked(self):
        self.onSaveButtonClicked()
        data = self.getDataFromEdits()
        dataFile = open("processData.json", "w")
        dataFile.write(json.dumps(data, indent = 4))
        dataFile.close()
        self.cs.commandRequestToSend = commands.REQUEST_RELOADDATA
        self.disableWidgets()

    def onComboBoxChanged(self):
        name = self.ui.comboBox.currentText()
        data = self.getProcessDataByName(name)
        self.refreshDataEdits(data)

    def onSaveButtonClicked(self):
        data = self.getDataFromEdits()
        updated = False
        #update allProcessData, if name already exists
        for processData in self.allProcessData:
            if data["name"] == processData["name"]:
                processData.update(data)
                updated = True
        #append data to processData, if name not exists
        if not updated:
            self.allProcessData.append(data)
            self.ui.comboBox.addItem(data["name"])
        #select new combobox index
        index = self.ui.comboBox.findText(data["name"])
        self.ui.comboBox.setCurrentIndex(index)
        #save data to file
        dataFile = open("allProcessData.json", "w")
        dataFile.write(json.dumps(self.allProcessData, indent = 4))
        dataFile.close()

    def onDeleteButtonClicked(self):
        data = self.getDataFromEdits()
        #update allProcessData
        self.allProcessData.remove(data)
        #update combobox and jump to first item
        index = self.ui.comboBox.findText(data["name"])
        self.ui.comboBox.removeItem(index)
        self.ui.comboBox.setCurrentIndex(0)
        #write allProcessData to file
        dataFile = open("allProcessData.json", "w")
        dataFile.write(json.dumps(self.allProcessData))
        dataFile.close()

    def onDriveToX1ButtonClicked(self):
        self.cs.commandRequestToSend = commands.REQUEST_DRIVEX1
        self.disableWidgets()

    def onDriveToX2ButtonClicked(self):
        self.cs.commandRequestToSend = commands.REQUEST_DRIVEX2
        self.disableWidgets()

    def onDriveToX3ButtonClicked(self):
        self.cs.commandRequestToSend = commands.REQUEST_DRIVEX3
        self.disableWidgets()

    def onStartButtonClicked(self):
        self.cs.commandRequestToSend = commands.REQUEST_STARTDRILLING
        self.disableWidgets()

    def onStopButtonClicked(self):
        self.cs.sendInterrupt = True
        self.disableWidgets()

    def disableWidgets(self):
        self.ui.comboBox.setEnabled(False)

        self.ui.label.setEnabled(False)
        self.ui.label_2.setEnabled(False)
        self.ui.label_3.setEnabled(False)
        self.ui.label_4.setEnabled(False)
        self.ui.label_5.setEnabled(False)
        self.ui.label_6.setEnabled(False)
        self.ui.label_7.setEnabled(False)
        self.ui.label_10.setEnabled(False)
        self.ui.label_11.setEnabled(False)
        self.ui.label_12.setEnabled(False)
        self.ui.label_13.setEnabled(False)
        self.ui.label_14.setEnabled(False)

        self.ui.dataNameEdit.setEnabled(False)
        self.ui.extraEdit.setEnabled(False)
        self.ui.holeCountEdit.setEnabled(False)
        self.ui.rotorPositionEdit.setEnabled(False)
        self.ui.rotorSpeedEdit.setEnabled(False)
        self.ui.x1Edit.setEnabled(False)
        self.ui.x2Edit.setEnabled(False)
        self.ui.x3Edit.setEnabled(False)
        self.ui.v1Edit.setEnabled(False)
        self.ui.v2Edit.setEnabled(False)
        self.ui.v3Edit.setEnabled(False)
        self.ui.v4Edit.setEnabled(False)

        self.ui.saveDataButton.setEnabled(False)
        self.ui.saveDataAndLoadButton.setEnabled(False)
        self.ui.deleteDataButton.setEnabled(False)
        self.ui.driveX1Button.setEnabled(False)
        self.ui.driveX2Button.setEnabled(False)
        self.ui.driveX3Button.setEnabled(False)
        self.ui.startButton.setEnabled(False)

    def enableWidgets(self):
        self.ui.comboBox.setEnabled(True)

        self.ui.label.setEnabled(True)
        self.ui.label_2.setEnabled(True)
        self.ui.label_3.setEnabled(True)
        self.ui.label_4.setEnabled(True)
        self.ui.label_5.setEnabled(True)
        self.ui.label_6.setEnabled(True)
        self.ui.label_7.setEnabled(True)
        self.ui.label_10.setEnabled(True)
        self.ui.label_11.setEnabled(True)
        self.ui.label_12.setEnabled(True)
        self.ui.label_13.setEnabled(True)
        self.ui.label_14.setEnabled(True)

        self.ui.dataNameEdit.setEnabled(True)
        self.ui.extraEdit.setEnabled(True)
        self.ui.holeCountEdit.setEnabled(True)
        self.ui.rotorPositionEdit.setEnabled(True)
        self.ui.rotorSpeedEdit.setEnabled(True)
        self.ui.x1Edit.setEnabled(True)
        self.ui.x2Edit.setEnabled(True)
        self.ui.x3Edit.setEnabled(True)
        self.ui.v1Edit.setEnabled(True)
        self.ui.v2Edit.setEnabled(True)
        self.ui.v3Edit.setEnabled(True)
        self.ui.v4Edit.setEnabled(True)

        self.ui.saveDataButton.setEnabled(True)
        self.ui.saveDataAndLoadButton.setEnabled(True)
        self.ui.deleteDataButton.setEnabled(True)
        self.ui.driveX1Button.setEnabled(True)
        self.ui.driveX2Button.setEnabled(True)
        self.ui.driveX3Button.setEnabled(True)
        self.ui.startButton.setEnabled(True)

    def getDataFromEdits(self):
        try:
            return {"name" : str(self.ui.dataNameEdit.text()),
                    "edit" : str(self.ui.extraEdit.text()),
                    "holeNumber" : int(self.ui.holeCountEdit.text()),
                    "rotorSteps" : int(self.ui.rotorPositionEdit.text()),
                    "rotorOperationSpeed" : int(self.ui.rotorSpeedEdit.text()),
                    "rotorOperationMode" : 0,
                    "x1" : int(self.ui.x1Edit.text()),
                    "x2" : int(self.ui.x2Edit.text()),
                    "x3" : int(self.ui.x3Edit.text()),
                    "x4" : int(self.ui.x1Edit.text()),
                    "x5" : 0,
                    "v1" : int(self.ui.v1Edit.text()),
                    "v2" : int(self.ui.v2Edit.text()),
                    "v3" : int(self.ui.v3Edit.text()),
                    "v4" : int(self.ui.v4Edit.text()),
                    "v5" : 10000,
                    "mode1" : 1,
                    "mode2" : 1,
                    "mode3" : 1,
                    "mode4" : 1,
                    "mode5" : 1}
        except ValueError:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Ungueltige Eingabewerte!")
            raise ValueError

    def refreshDataEdits(self, processData):
        if processData != None:
            self.ui.dataNameEdit.setText(processData["name"])
            self.ui.extraEdit.setText(processData["edit"])
            self.ui.x1Edit.setText(str(processData["x1"]))
            self.ui.x2Edit.setText(str(processData["x2"]))
            self.ui.x3Edit.setText(str(processData["x3"]))
            self.ui.v1Edit.setText(str(processData["v1"]))
            self.ui.v2Edit.setText(str(processData["v2"]))
            self.ui.v3Edit.setText(str(processData["v3"]))
            self.ui.v4Edit.setText(str(processData["v4"]))
            self.ui.rotorSpeedEdit.setText(str(processData["rotorOperationSpeed"]))
            self.ui.rotorPositionEdit.setText(str(processData["rotorSteps"]))
            self.ui.holeCountEdit.setText(str(processData["holeNumber"]))
        else:
            self.ui.dataNameEdit.setText("")
            self.ui.extraEdit.setText("")
            self.ui.x1Edit.setText("")
            self.ui.x2Edit.setText("")
            self.ui.x3Edit.setText("")
            self.ui.v1Edit.setText("")
            self.ui.v2Edit.setText("")
            self.ui.v3Edit.setText("")
            self.ui.v4Edit.setText("")
            self.ui.rotorSpeedEdit.setText("")
            self.ui.rotorPositionEdit.setText("")
            self.ui.holeCountEdit.setText("")

    def getProcessDataByName(self, name):
        for processData in self.allProcessData:
            if processData["name"] == name:
                return processData

    def closeEvent(self):
        os.kill(os.getpid(), 15)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Gui()
    app.aboutToQuit.connect(window.closeEvent)
    sys.exit(app.exec_())
