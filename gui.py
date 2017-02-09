import sys
import json
import logging
import communicationUtilities
import commands
import os
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot

class Gui(QtGui.QDialog):
    """The gui to configure the driller.

    Attributes:
        * receivedResponse: The signal which is emmited if the gui has received an answer
        * ui: The interface
        * cs: The sender which sends commands to the driller
        * allowedToSend: A flag which indicates, if the gui is allowed to send commands
        * allProcessData: A list of dictionarys which stores all process data. See :meth:`loadAllProcessData`
        * allProcessDataFileName: The json file where all process data are stored
    """
    receivedResponse = pyqtSignal(str)

    LINEAR_BALL_SCREW_LEAD = float(6)
    ELECTRONIC_GEAR_A = float(1)
    ELECTRONIC_GEAR_B = float(1)
    STEPS_PER_RESOLUTION = float(40000)

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("Interface.ui")

        self.allProcessDataFileName = "allProcessData.json"
        self.processDataFileName = "processData.json"
        self.loadAllProcessData()

        logging.basicConfig(level = logging.DEBUG)

        self.cs = communicationUtilities.CommandSender(self)
        self.cs.start()
        self.allowedToSend = True

        self.receivedResponse.connect(self.onReceiveResponseEvent)

        #setup combobox
        for processData in self.allProcessData:
            self.ui.comboBox.addItem(processData["name"])
        currentProcessDataName = self.getCurrentlyUsedProcessdataName()
        if currentProcessDataName != "":
            self.ui.comboBox.setCurrentIndex(self.ui.comboBox.findText(currentProcessDataName))
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

    def getCurrentlyUsedProcessdataName(self):
        """Gets currently used processdata name from processData.json"""
        try:
            data = open(self.processDataFileName, "r")
            processData = json.loads(data.read())
            return processData['name']
        except:
            return ""

    def loadAllProcessData(self):
        """Loads all process data from the json file and stores them into allProcessData.

        A valid json file is descriped in :mod:`bohrvorrichtung`.
        
        """
        data = open(self.allProcessDataFileName, "r")
        self.allProcessData = json.loads(data.read())
        logging.info("Loaded all process data:")
        logging.info(str(self.allProcessData))
        data.close()

    @pyqtSlot(str)
    def onReceiveResponseEvent(self, response):
        """Gets called when a response was received. Displays respone information
        and enables widges.
        """
        logging.info(response)
        if response == commands.INTERRUPT:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Bohrvorrichtung wurde gestoppt!")
        if response == commands.RESPONSE_FAIL:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Operation fehlgeschlagen!")
        if response == commands.RESPONSE_INVALID_REQUEST:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", "Ungueltige Anforderung!")
        self.enableWidgets()

    def onResponse(self, response):
        self.receivedResponse.emit(response)

    def onSaveDataAndLoadButtonClicked(self):
        """Saves process data and sends reload command."""
        self.onSaveButtonClicked()
        data = self.getDataFromEdits()
        dataFile = open(self.processDataFileName, "w")
        dataFile.write(json.dumps(data, indent = 4, sort_keys = True))
        dataFile.close()
        self.cs.commandRequestToSend = commands.REQUEST_RELOADDATA
        self.disableWidgets()

    def onComboBoxChanged(self):
        """Updates gui after combo box index change."""
        name = self.ui.comboBox.currentText()
        data = self.getProcessDataByName(name)
        self.refreshDataEdits(data)

    def onSaveButtonClicked(self):
        """Saves current process data to allProcessData and writes it to file."""
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
        dataFile = open(self.allProcessDataFileName, "w")
        dataFile.write(json.dumps(self.allProcessData, indent = 4, sort_keys = True))
        dataFile.close()

    def onDeleteButtonClicked(self):
        """Deletes current process data and updates allProcess data file."""
        data = self.getDataFromEdits()
        #update allProcessData
        self.allProcessData.remove(self.getDataFromDataName(data["name"]))
        #update combobox and jump to first item
        index = self.ui.comboBox.findText(data["name"])
        self.ui.comboBox.removeItem(index)
        self.ui.comboBox.setCurrentIndex(0)
        #write allProcessData to file
        dataFile = open(self.allProcessDataFileName, "w")
        dataFile.write(json.dumps(self.allProcessData, indent = 4, sort_keys = True))
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
        """Disables all widgets."""
        self.ui.comboBox.setEnabled(False)

        self.ui.label.setEnabled(False)
        self.ui.label_3.setEnabled(False)
        self.ui.label_4.setEnabled(False)
        self.ui.label_5.setEnabled(False)
        self.ui.label_6.setEnabled(False)
        self.ui.label_7.setEnabled(False)
        self.ui.label_8.setEnabled(False)
        self.ui.label_9.setEnabled(False)
        self.ui.label_10.setEnabled(False)
        self.ui.label_11.setEnabled(False)
        self.ui.label_12.setEnabled(False)
        self.ui.label_13.setEnabled(False)
        self.ui.label_14.setEnabled(False)

        self.ui.isReverse.setEnabled(False)

        self.ui.dataNameEdit.setEnabled(False)
        self.ui.rotorOffsetEdit.setEnabled(False)
        self.ui.holeCountEdit.setEnabled(False)
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
        """Enables all widgets."""
        self.ui.comboBox.setEnabled(True)

        self.ui.label.setEnabled(True)
        self.ui.label_3.setEnabled(True)
        self.ui.label_4.setEnabled(True)
        self.ui.label_5.setEnabled(True)
        self.ui.label_6.setEnabled(True)
        self.ui.label_7.setEnabled(True)
        self.ui.label_8.setEnabled(True)
        self.ui.label_9.setEnabled(True)
        self.ui.label_10.setEnabled(True)
        self.ui.label_11.setEnabled(True)
        self.ui.label_12.setEnabled(True)
        self.ui.label_13.setEnabled(True)
        self.ui.label_14.setEnabled(True)

        self.ui.isReverse.setEnabled(True)

        self.ui.dataNameEdit.setEnabled(True)
        self.ui.rotorOffsetEdit.setEnabled(True)
        self.ui.holeCountEdit.setEnabled(True)
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

    def getDataFromDataName(self, name):
        for processData in self.allProcessData:
            if processData["name"] == name:
                return processData
        return None

    def getDataFromEdits(self):
        """Reads from input edits.

        Args:
            None

        Returns:
            A dict with process data information. See :meth:`loadAllProcessData`

        Raises:
            ValueError
        """
        try:
            maxLinearSpeed = 100
            minLinearSpeed = 0.1
            maxLinearPosition = 120
            minLinearPosition = 0
            maxRotorSpeed = 50000
            minRotorSpeed = 1
            maxRotorOffset = 360
            minRotorOffset = -360
            maxHoleNumber = 1000
            minHoleNumber = 1
            name = str(self.ui.dataNameEdit.text())
            rotorOffset = float(self.ui.rotorOffsetEdit.text())
            if rotorOffset > maxRotorOffset:
                raise ValueError("Angabe fuer Rotoroffset zu gross!")
            elif rotorOffset < minRotorOffset:
                raise ValueError("Angabe fuer Rotoroffset zu klein!")
            rotorOffsetSpeed = 500
            holeNumber = int(self.ui.holeCountEdit.text())
            if holeNumber > maxHoleNumber:
                raise ValueError("Angabe fuer Lochzahl zu gross!")
            elif holeNumber < minHoleNumber:
                raise ValueError("Angabe fuer Lochzahl zu klein!")
            rotorOperationSpeed = float(self.ui.rotorSpeedEdit.text())
            if rotorOperationSpeed > maxRotorSpeed:
                raise ValueError("Angabe fuer Rotorgeschwindigkeit zu gross!")
            elif rotorOperationSpeed < minRotorSpeed:
                raise ValueError("Angabe fuer Rotorgeschwindigkeit zu klein!")
            rotorOperationMode = 0
            x1 = float(self.ui.x1Edit.text())
            if x1 > maxLinearPosition:
                raise ValueError("Angabe fuer Position 1 zu gross!")
            elif x1 < minLinearPosition:
                raise ValueError("Angabe fuer Position 1 zu klein!")
            x2 = float(self.ui.x2Edit.text())
            if x2 > maxLinearPosition:
                raise ValueError("Angabe fuer Position 2 zu gross!")
            elif x2 < minLinearPosition:
                raise ValueError("Angabe fuer Position 2 zu klein!")
            x3 = float(self.ui.x3Edit.text())
            if x3 > maxLinearPosition:
                raise ValueError("Angabe fuer Position 3 zu gross!")
            elif x3 < minLinearPosition:
                raise ValueError("Angabe fuer Position 3 zu klein!")
            x4 = float(self.ui.x1Edit.text())
            if x4 > maxLinearPosition:
                raise ValueError("Angabe fuer Position 4 zu gross!")
            elif x4 < minLinearPosition:
                raise ValueError("Angabe fuer Position 4 zu klein!")
            x5 = 0
            v1 = float(self.ui.v1Edit.text())
            if v1 > maxLinearSpeed:
                raise ValueError("Angabe fuer Geschwindigkeit 1 zu gross!")
            elif v1 < minLinearSpeed:
                raise ValueError("Angabe fuer Geschwindigkeit 1 zu klein!")
            v2 = float(self.ui.v2Edit.text())
            if v2 > maxLinearSpeed:
                raise ValueError("Angabe fuer Geschwindigkeit 2 zu gross!")
            elif v2 < minLinearSpeed:
                raise ValueError("Angabe fuer Geschwindigkeit 2 zu klein!")
            v3 = float(self.ui.v3Edit.text())
            if v3 > maxLinearSpeed:
                raise ValueError("Angabe fuer Geschwindigkeit 3 zu gross!")
            elif v3 < minLinearSpeed:
                raise ValueError("Angabe fuer Geschwindigkeit 3 zu klein!")
            v4 = float(self.ui.v4Edit.text())
            if v4 > maxLinearSpeed:
                raise ValueError("Angabe fuer Rueckfahrgeschwindigkeit zu gross!")
            elif v4 < minLinearSpeed:
                raise ValueError("Angabe fuer Rueckfahrgeschwindigkeit zu klein!")
            v5 = 10000
            mode1 = 1
            mode2 = 1
            mode3 = 1
            mode4 = 1
            mode5 = 1
            rotorSteps = int(self.STEPS_PER_RESOLUTION / holeNumber)
            if self.ui.isReverse.isChecked():
                rotorSteps = rotorSteps * (-1)
            return {"name" : name,
                    "rotorOffset" : self.degreeToSteps(rotorOffset),
                    "rotorOffsetSpeed" : rotorOffsetSpeed,
                    "holeNumber" : holeNumber,
                    "rotorSteps" : rotorSteps,
                    "rotorOperationSpeed" : self.degreePerSecondToHz(rotorOperationSpeed),
                    "rotorOperationMode" : 0,
                    "x1" : self.mmToSteps(x1),
                    "x2" : self.mmToSteps(x2),
                    "x3" : self.mmToSteps(x3),
                    "x4" : self.mmToSteps(x4),
                    "x5" : self.mmToSteps(x5),
                    "v1" : self.mmPerSecondToHz(v1),
                    "v2" : self.mmPerSecondToHz(v2),
                    "v3" : self.mmPerSecondToHz(v3),
                    "v4" : self.mmPerSecondToHz(v4),
                    "v5" : v5,
                    "mode1" : mode1,
                    "mode2" : mode2,
                    "mode3" : mode3,
                    "mode4" : mode4,
                    "mode5" : mode5}
        except ValueError as e:
            w = QtGui.QWidget()
            QtGui.QMessageBox.warning(w, "Warnung!", e.message)
            raise ValueError

    def refreshDataEdits(self, processData):
        """Refreshes input edits with given values.

        Args:
            * processData

        Returns:
            None

        Raises:
            None
        """
        if processData != None:
            self.ui.dataNameEdit.setText(processData["name"])
            self.ui.x1Edit.setText("%.2f" % (self.stepsToMM(processData["x1"])))
            self.ui.x2Edit.setText("%.2f" % (self.stepsToMM(processData["x2"])))
            self.ui.x3Edit.setText("%.2f" % (self.stepsToMM(processData["x3"])))
            self.ui.v1Edit.setText("%.2f" % (self.hzToMMPerSecond(processData["v1"])))
            self.ui.v2Edit.setText("%.2f" % (self.hzToMMPerSecond(processData["v2"])))
            self.ui.v3Edit.setText("%.2f" % (self.hzToMMPerSecond(processData["v3"])))
            self.ui.v4Edit.setText("%.2f" % (self.hzToMMPerSecond(processData["v4"])))
            self.ui.rotorSpeedEdit.setText("%.2f" % (self.hzToDegreePerSecond(processData["rotorOperationSpeed"])))
            self.ui.holeCountEdit.setText(str(processData["holeNumber"]))
            self.ui.rotorOffsetEdit.setText("%.2f" % (self.stepsToDegree(processData["rotorOffset"])))
            if processData["rotorSteps"] < 0:
                self.ui.isReverse.setChecked(True)
            else:
                self.ui.isReverse.setChecked(False)
        else:
            self.ui.dataNameEdit.setText("")
            self.ui.rotorOffsetEdit.setText("")
            self.ui.x1Edit.setText("")
            self.ui.x2Edit.setText("")
            self.ui.x3Edit.setText("")
            self.ui.v1Edit.setText("")
            self.ui.v2Edit.setText("")
            self.ui.v3Edit.setText("")
            self.ui.v4Edit.setText("")
            self.ui.rotorSpeedEdit.setText("")
            self.ui.holeCountEdit.setText("")
            self.ui.isReverse.setChecked(False)

    def getProcessDataByName(self, name):
        for processData in self.allProcessData:
            if processData["name"] == name:
                return processData

    def mmPerSecondToHz(self, speed):
        """Transforms speed from mm/s to Hz."""
        resolution = 1000 * (self.ELECTRONIC_GEAR_B / self.ELECTRONIC_GEAR_A)
        minimumTravelAmount = self.LINEAR_BALL_SCREW_LEAD / resolution
        result = speed / minimumTravelAmount
        return int(result)

    def mmToSteps(self, position):
        """Transforms position from mm to steps."""
        resolution = 1000 * (self.ELECTRONIC_GEAR_B / self.ELECTRONIC_GEAR_A)
        minimumTravelAmount = self.LINEAR_BALL_SCREW_LEAD / resolution
        result = position / minimumTravelAmount
        return int(result)

    def hzToMMPerSecond(self, speed):
        """Transforms speed from hz to mm/s."""
        resolution = 1000 * self.ELECTRONIC_GEAR_B / self.ELECTRONIC_GEAR_A
        minimumTravelAmount = self.LINEAR_BALL_SCREW_LEAD / resolution
        result = speed * minimumTravelAmount
        return float(result)

    def stepsToMM(self, position):
        """Transforms position from steps to mm."""
        resolution = 1000 * (self.ELECTRONIC_GEAR_B / self.ELECTRONIC_GEAR_A)
        minimumTravelAmount = self.LINEAR_BALL_SCREW_LEAD / resolution
        result = position * minimumTravelAmount
        return float(result)

    def degreeToSteps(self, angle):
        """Transforms degree to steps for the rotor."""
        stepsPerDegree = self.STEPS_PER_RESOLUTION / 360.0
        result = int(stepsPerDegree * angle)
        return result

    def stepsToDegree(self, position):
        """Transforms steps to degree for the rotor."""
        degreePerStep = 360.0 / self.STEPS_PER_RESOLUTION
        result = float(degreePerStep * position)
        return result

    def degreePerSecondToHz(self, anglePerSecond):
        """Transforms degrees per second to hz for the rotor."""
        stepsPerDegree = self.STEPS_PER_RESOLUTION / 360.0
        result = int(stepsPerDegree * anglePerSecond)
        return result

    def hzToDegreePerSecond(self, speed):
        """Transforms hz to steps per second for the rotor."""
        degreePerStep = 360.0 / self.STEPS_PER_RESOLUTION
        result = float(degreePerStep * speed)
        return result

    def closeEvent(self):
        os.kill(os.getpid(), 15)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Gui()
    app.aboutToQuit.connect(window.closeEvent)
    sys.exit(app.exec_())
