import sys
import json
import logging
from PyQt4 import QtCore, QtGui, uic

class Gui(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Interface.ui")
        self.loadAllProcessData()
        self.ui.comboBox.addItems(self.processDataNames)
        self.onComboBoxChanged()
        self.ui.comboBox.currentIndexChanged.connect(self.onComboBoxChanged)
        self.ui.saveDataButton.clicked.connect(self.onSaveButtonClicked)
        self.ui.deleteDataButton.clicked.connect(self.onDeleteButtonClicked)
        self.ui.show()

    def loadAllProcessData(self):
        data = open("allProcessData.json", "r")
        self.allProcessData = json.loads(data.read())
        self.processDataNames = []
        for processData in self.allProcessData:
            self.processDataNames.append(processData["name"])
        logging.info("Loaded all process data:")
        logging.info(str(self.allProcessData))
        data.close()

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
            self.processDataNames.append(data["name"])
            self.ui.comboBox.addItem(data["name"])
        #select new combobox index
        index = self.ui.comboBox.findText(data["name"])
        self.ui.comboBox.setCurrentIndex(index)
        #save data to file
        dataFile = open("allProcessData.json", "w")
        dataFile.write(json.dumps(self.allProcessData))
        dataFile.close()

    def onDeleteButtonClicked(self):
        data = self.getDataFromEdits()
        #update allProcessData
        self.allProcessData.remove(data)
        #update processDataNames
        self.processDataNames.remove(data["name"])
        #update combobox and jump to first item
        index = self.ui.comboBox.findText(data["name"])
        self.ui.comboBox.removeItem(index)
        self.ui.comboBox.setCurrentIndex(0)
        #write allProcessData to file
        dataFile = open("allProcessData.json", "w")
        dataFile.write(json.dumps(self.allProcessData))
        dataFile.close()

    def getDataFromEdits(self):
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

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Gui()
    sys.exit(app.exec_())
