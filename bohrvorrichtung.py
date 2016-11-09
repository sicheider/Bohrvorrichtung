import stepperMotor
import communicationUtilities
import os
import commands
import time

class Bohrvorrichtung(object):
    def __init__(self):
        self.rotor = stepperMotor.StepperMotor("rotor", 5, self)
        self.linear = stepperMotor.StepperMotor("linear", 6, self)
        self.operationPositions = [15000, 16100, 15000]
        self.operationSpeeds = [15000, 125, 2000]
        self.operationModes = [1, 1, 1]
        self.holeNumer = 32
        self.rotorSteps = 1250
        self.writeProcessParameters()
        self.isInterrupted = False
        self.mainLoopWaitTime = 0.1
        self.cr = communicationUtilities.CommandReceiver(self)
        self.connections = []
        self.ca.start()
        self.sayHello()

    def writeProcessParameters(self):
        self.rotor.writeOperationPosition(self.rotorSteps, 0)
        self.rotor.writeOperationMode(0, 0)
        for i in range(0, 3):
            self.linear.writeOperationPosition(self.operationPositions[i], i)
            self.linear.writeOperationSpeed(self.operationSpeeds[i], i)
            self.linear.writeOperationMode(self.operationModes[i], i)

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
