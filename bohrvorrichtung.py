import stepperMotor
import communicationUtilities
import os
import commands
import time
import json
import logging

class Bohrvorrichtung(object):
    """The actual driller. Starts listening on commands when :meth:`start` is called!

    Attributes:
        * rotor: The rotor stepper motor
        * linear: The linear stepper motor
        * isInterrupted: Flag if driller is interrupted or not
        * mainLoopWaitTime: Timeout for mainloop
        * cr: Instance of CommandReceiver; Handles all incoming command requests
    """
    def __init__(self):
        """Constructor. Initializes everythin."""
        logging.basicConfig(level = logging.DEBUG)
        self.rotor = stepperMotor.StepperMotor("rotor", 5, self)
        self.linear = stepperMotor.StepperMotor("linear", 6, self)
        self.processDataToDevice()
        self.isInterrupted = False
        self.mainLoopWaitTime = 0.1
        self.cr = communicationUtilities.CommandReceiver(self)
        self.cr.start()
        self.sayHello()

    def loadProcessData(self):
        """Loads process data from json file. The json file must define:

        Attributes:
            * holeNumber: The ammount of holes
            * rotorSteps: The steps for each rotor move
            * rotorOperationSpeed
            * rotorOperationMode
            * x1: The position where drilling starts
            * x2: The middleposition of drilling 
            * x3: The position where drilling ends
            * x4: The position where drilling starts
            * x5: Nullposition
            * v1: Speed to x1
            * v2: Speed to x2
            * v3: Speed to x3
            * v4: Speed to x4
            * v5: Speed to x5
            * mode1
            * mode2
            * mode3
            * mode4
            * mode5
        """
        data = open("processData.json", "r")
        self.processData = json.loads(data.read())
        self.holeNumer = self.processData["holeNumber"]
        logging.info("Loaded process data:")
        logging.info(str(self.processData))
        data.close()
        self.linearDriveToSpeed = 2000

    def writeProcessData(self):
        """Writes process data to stepper motor registers."""
        logging.debug("Writing process data to devices")
        self.rotor.writeOperationPosition(self.processData["rotorSteps"], 0)
        self.rotor.writeOperationSpeed(self.processData["rotorOperationSpeed"], 0)
        #better dont touch this value
        #self.rotor.writeOperationMode(self.processData["rotorOperationMode"], 0)
        self.linear.writeOperationPosition(self.processData["x1"], 0)
        self.linear.writeOperationPosition(self.processData["x2"], 1)
        self.linear.writeOperationPosition(self.processData["x3"], 2)
        self.linear.writeOperationPosition(self.processData["x4"], 3)
        self.linear.writeOperationPosition(self.processData["x5"], 4)
        self.linear.writeOperationSpeed(self.processData["v1"], 0)
        self.linear.writeOperationSpeed(self.processData["v2"], 1)
        self.linear.writeOperationSpeed(self.processData["v3"], 2)
        self.linear.writeOperationSpeed(self.processData["v4"], 3)
        self.linear.writeOperationSpeed(self.processData["v5"], 4)
        self.linear.writeOperationMode(self.processData["mode1"], 0)
        self.linear.writeOperationMode(self.processData["mode2"], 1)
        self.linear.writeOperationMode(self.processData["mode3"], 2)
        self.linear.writeOperationMode(self.processData["mode4"], 3)
        self.linear.writeOperationMode(self.processData["mode5"], 4)

    def processDataToDevice(self):
        """Loads and writes process data."""
        self.loadProcessData()
        self.writeProcessData()

    def finishCommand(self):
        self.isInterrupted = False

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
        self.linear.goHome()
        self.rotor.goHome()
        self.linear.startOperation(0)
        for _ in range(0, self.holeNumer):
            self.linear.startOperation(1)
            self.linear.startOperation(2)
            self.linear.startOperation(3)
            self.rotor.startOperation(0)
        self.linear.goHome()
        self.finishCommand()

    def fakeDrillingLinear(self):
        """Drives linear to given position."""
        logging.debug("Driving linear!")
        self.linear.startOperation(4)
        for i in range(0, position):
            self.linear.startOperation(i)

    def driveLinearTo(self, position):
        """Drives linear to given position."""
        logging.debug("Driving linear to: " + str(position))
        self.linear.writeOperationSpeed(self.linearDriveToSpeed, position - 1)
        self.linear.writeOperationMode(1, position - 1)
        self.linear.startOperation(position - 1)
        self.processDataToDevice()
        self.finishCommand()

    def handleCommand(self, command):
        """Parses a incomming command and performs an action.
        
        Returns:
            SUCCESS, FAIL or INVALID_REQUEST
        """
        if command == commands.REQUEST_STARTDRILLING:
            try:
                self.startDrilling()
                return commands.RESPONSE_SUCCESS
            except KeyboardInterrupt:
                os.kill(os.getpid(), 9)
            except:
                logging.exception("Error while drilling!")
                return commands.RESPONSE_FAIL
        elif command == commands.REQUEST_RELOADDATA:
            try:
                self.processDataToDevice()
                return commands.RESPONSE_SUCCESS
            except:
                logging.exception("Error while loading process data!")
                return commands.RESPONSE_FAIL
        elif command == commands.REQUEST_DRIVEX1:
            try:
                self.driveLinearTo(1)
                return commands.RESPONSE_SUCCESS
            except:
                logging.exception("Error while positioning linear!")
                return commands.RESPONSE_FAIL
        elif command == commands.REQUEST_DRIVEX2:
            try:
                self.driveLinearTo(2)
                return commands.RESPONSE_SUCCESS
            except:
                logging.exception("Error while positioning linear!")
                return commands.RESPONSE_FAIL
        elif command == commands.REQUEST_DRIVEX3:
            try:
                self.driveLinearTo(3)
                return commands.RESPONSE_SUCCESS
            except:
                logging.exception("Error while positioning linear!")
                return commands.RESPONSE_FAIL
        else:
            logging.warning("Invalid request:")
            logging.warning(command)
            return commands.RESPONSE_INVALID_REQUEST

    def handleInterrupt(self):
        """Interrupts the driller. All motors are STOPPED."""
        logging.debug("Device interrupted")
        self.rotor.stopMoving()
        self.linear.stopMoving()

    def start(self):
        """Starts mainloop and listens to incoming commands.
        For valid commands see :mod:`commands`"""
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
