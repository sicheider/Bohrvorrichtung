import stepperMotor
import communicationUtilities
import os
import commands
import time
import json
import logging

class Bohrvorrichtung(object):
    def __init__(self):
        self.rotor = stepperMotor.StepperMotor("rotor", 5, self)
        self.linear = stepperMotor.StepperMotor("linear", 6, self)
        self.writeProcessData()
        self.isInterrupted = False
        self.mainLoopWaitTime = 0.1
        self.cr = communicationUtilities.CommandReceiver(self)
        self.sayHello()
        self.ca.start()

    def loadProcessData(self):
        data = open("processdata.json", "r")
        self.processData = json.loads(data.read())
        self.holeNumer = self.processData["holeNumer"]
        logging.info("Loaded process data:")
        logging.info(str(self.processData))
        data.close()

    def writeProcessData(self):
        self.rotor.writeOperationPosition(self.processData["rotorSteps"], 0)
        self.rotor.writeOperationSpeed(self.processData["rotorOperationSpeed"], 0)
        self.rotor.writeOperationMode(self.processData["rotorOperationMode"], 0)
        self.linear.writeOperationPosition(self.processData["x1"], 0)
        self.linear.writeOperationPosition(self.processData["x2"], 1)
        self.linear.writeOperationPosition(self.processData["x3"], 2)
        self.linear.writeOperationSpeed(self.processData["v1"], 0)
        self.linear.writeOperationSpeed(self.processData["v2"], 1)
        self.linear.writeOperationSpeed(self.processData["v3"], 2)
        self.linear.writeOperationMode(self.processData["mode1"], 0)
        self.linear.writeOperationMode(self.processData["mode2"], 1)
        self.linear.writeOperationMode(self.processData["mode3"], 2)

    def processDataToDevice(self):
        self.loadProcessData()
        self.writeProcessData()

    def sayHello(self):
        self.linear.goHome()
        self.rotor.startOperation(0)
        self.rotor.startOperation(0)
        self.rotor.goHome()

    def startDrilling(self):
        self.rotor.goHome()
        self.linear.startOperation(0)
        for _ in range(0, self.holeNumer):
            self.linear.startOperation(1)
            self.linear.startOperation(2)
            self.rotor.startOperation(0)
        self.linear.goHome()

    def handleCommand(self, command):
        if command == commands.START_DRILLING:
            try:
                self.startDrilling()
                return commands.RESPONSE_SUCCESS
            except KeyboardInterrupt:
                os.kill(os.getpid(), 9)
            except IOError:
                return commands.RESPONSE_FAIL
        else:
            return commands.INVALID_REQUEST

    def handleInterrupt(self):
        self.rotor.stopMoving()
        self.linear.stopMoving()
        self.isInterrupted = False

    def start(self):
        while True:
            try:
                time.sleep(self.mainLoopWaitTime)
                commandRequest, con = self.cr.commandRequests.popleft()
                result = self.handleCommand(commandRequest)
                self.cr.commandResponses.append((result, con))
            except IndexError:
                pass
            except KeyboardInterrupt:
                os.kill(os.getpid(), 9)
            
if __name__ == "__main__":
    bohrvorrichtung = Bohrvorrichtung()
    bohrvorrichtung.start()
