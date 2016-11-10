import stepperMotor
import communicationUtilities
import os
import commands
import time
import json
import logging

class Bohrvorrichtung(object):
    """The actual driller.

    Attributes:
        * rotor: The rotor stepper motor
        * linear: The linear stepper motor
        * isInterrupted: Flag if driller is interrupted or not
        * mainLoopWaitTime: Timeout for mainloop
        * cr: Instance of CommandReceiver; Handles all incoming command requests
    """
    def __init__(self):
        """Constructor. Initializes everythin."""
        self.rotor = stepperMotor.StepperMotor("rotor", 5, self)
        self.linear = stepperMotor.StepperMotor("linear", 6, self)
        self.processDataToDevice()
        self.isInterrupted = False
        self.mainLoopWaitTime = 0.1
        self.cr = communicationUtilities.CommandReceiver(self)
        self.sayHello()

    def loadProcessData(self):
        """Loads process data from json file. The json file must define:

        Attributes:
            * holeNumber: The ammount of holes
            * rotorSteps: The steps for each rotor move
            * rotorOperationSpeed
            * rotorOperationMode
            * x1: The position where drilling starts
            * x2: The position where drilling ends
            * x3: The position where drilling starts
            * x4: Nullposition
            * v1: Speed to x1
            * v2: Speed to x2
            * v3: Speed to x3
            * v4: Speed to x4
            * mode1
            * mode2
            * mode3
            * mode4
        """
        data = open("processdata.json", "r")
        self.processData = json.loads(data.read())
        self.holeNumer = self.processData["holeNumer"]
        logging.info("Loaded process data:")
        logging.info(str(self.processData))
        data.close()

    def writeProcessData(self):
        """Writes process data to stepper motor registers."""
        logging.debug("Writing process data to devices")
        self.rotor.writeOperationPosition(self.processData["rotorSteps"], 0)
        self.rotor.writeOperationSpeed(self.processData["rotorOperationSpeed"], 0)
        self.rotor.writeOperationMode(self.processData["rotorOperationMode"], 0)
        self.linear.writeOperationPosition(self.processData["x1"], 0)
        self.linear.writeOperationPosition(self.processData["x2"], 1)
        self.linear.writeOperationPosition(self.processData["x3"], 2)
        self.linear.writeOperationPosition(self.processData["x4"], 3)
        self.linear.writeOperationSpeed(self.processData["v1"], 0)
        self.linear.writeOperationSpeed(self.processData["v2"], 1)
        self.linear.writeOperationSpeed(self.processData["v3"], 2)
        self.linear.writeOperationSpeed(self.processData["v4"], 3)
        self.linear.writeOperationMode(self.processData["mode1"], 0)
        self.linear.writeOperationMode(self.processData["mode2"], 1)
        self.linear.writeOperationMode(self.processData["mode3"], 2)
        self.linear.writeOperationMode(self.processData["mode4"], 3)

    def processDataToDevice(self):
        """Loads and writes process data."""
        self.loadProcessData()
        self.writeProcessData()

    def sayHello(self):
        """Process initial movement."""
        logging.debug("Saying hello")
        self.linear.goHome()
        self.rotor.startOperation(0)
        self.rotor.startOperation(0)
        self.rotor.goHome()

    def startDrilling(self):
        """Perform drilling process."""
        logging.debug("Start drilling")
        self.rotor.goHome()
        self.linear.startOperation(0)
        for _ in range(0, self.holeNumer):
            self.linear.startOperation(1)
            self.linear.startOperation(2)
            self.rotor.startOperation(0)
        self.linear.goHome()

    def handleCommand(self, command):
        """Parses a incomming command and performs an action.
        
        Returns:
            SUCCESS, FAIL or INVALID_REQUEST
        """
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
        """Interrupts the driller. All motors are STOPPED."""
        logging.debug("Device interrupted")
        self.rotor.stopMoving()
        self.linear.stopMoving()
        self.isInterrupted = False

    def start(self):
        """Starts mainloop and listens to incoming commands."""
        logging.info("Starting main loop")
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
