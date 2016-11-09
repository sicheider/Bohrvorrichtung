import minimalmodbus
import time
import serial
import logging

class StepperMotor(minimalmodbus.Instrument, object):
    def __init__(self, name, adress, master,
            serialPort = "/dev/ttyUSB0",
            baudrate = 19200,
            stopbits = 1,
            parity = serial.PARITY_NONE,
            timeout = 0.05,
            standardWaitTime = 0.02,
            waitForPingTime = 0.2,
            maxFailCounter = 50):
        minimalmodbus.BAUDRATE = baudrate
        minimalmodbus.STOPBITS = stopbits
        minimalmodbus.PARITY = parity
        minimalmodbus.TIMEOUT = timeout
        super(StepperMotor, self).__init__(serialPort, adress)
        self.waitForPingTime = waitForPingTime
        self.standardWaitTime = standardWaitTime
        self.maxFailCounter = maxFailCounter
        self.master = master

        self.inputRegister = 125
        self.outputRegister = 127
        #self.operationPositionUpperRegisters = range(1024, 1152, 2)
        self.operationPositionLowerRegisters = range(1025, 1153, 2)
        #self.operationSpeedUpperRegisters = range(1152, 1280, 2)
        self.operationSpeedLowerRegisters = range(1153, 1281, 2)
        self.operationModeRegisters = range(1281, 1409, 2)

        self.moveBitOutput = 13

        self.homeBitInput = 4
        self.startBitInput = 3
        self.stopBitInput = 5
        self.forwardBitInput = 14
        self.reverseBitInput = 15

        self.operationCount = 7
        self.name = name

    def getStatus(self, message):
        return ("[" + self.name + "] " + message)

    def getBitFromRegister(self, adress, bit):
        registerValue = self.readRegisterSafe(adress)
        if registerValue & 2**bit == 0:
            return False
        return True

    def writeRegisterSafe(self, adress, value):
        run = True
        failCounter = 0
        while run:
            try:
                if failCounter > self.maxFailCounter:
                    logging.warning(self.getStatus("Could not write to register!"))
                    raise IOError("Could not write to register!")
                super(StepperMotor, self).write_register(adress, value)
                run = False
            except IOError:
                failCounter = failCounter + 1
                logging.debug(self.getStatus("IOError while writing register!"))
                time.sleep(self.standardWaitTime)
            except ValueError as e:
                failCounter = failCounter + 1
                logging.debug(self.getStatus("ValueError while writing register!"))
                logging.debug(self.getStatus(e.message))
                time.sleep(self.standardWaitTime)

    def readRegisterSafe(self, adress):
        run = True
        failCounter = 0
        while run:
            try:
                if failCounter > self.maxFailCounter:
                    logging.warning(self.getStatus("Could not read from register!"))
                    raise IOError("Could not read from register!")
                return super(StepperMotor, self).read_register(adress)
            except IOError:
                failCounter = failCounter + 1
                logging.debug(self.getStatus("IOError while reading from register!"))
                time.sleep(self.standardWaitTime)
            except ValueError as e:
                failCounter = failCounter + 1
                logging.debug(self.getStatus("ValueError while reading from register!"))
                logging.debug(self.getStatus(e.message))
                time.sleep(self.standardWaitTime)

    def waitFor(self):
        logging.debug(self.getStatus("Waiting for operation to finish!"))
        run = True
        while run and not self.master.isInterrupted:
            move = self.getBitFromRegister(self.outputRegister, self.moveBitOutput)
            if not move:
                run = False
            time.sleep(self.waitForPingTime)
        if self.master.isInterrupted:
            self.master.handleInterrupt()
            return
        logging.debug(self.getStatus("Operation finished!"))
        time.sleep(self.standardWaitTime)

    def writeToInputRegister(self, value):
        self.writeRegisterSafe(self.inputRegister, value)
        time.sleep(self.standardWaitTime)
        self.writeRegisterSafe(self.inputRegister, 0)
        time.sleep(self.standardWaitTime)

    def goHome(self):
        self.printStatus("Going home")
        self.writeToInputRegister(2**self.homeBitInput)
        self.waitFor()

    def goForward(self):
        self.printStatus("Going forward")
        self.writeRegisterSafe(self.inputRegister, 2**self.forwardBitInput)

    def goReverse(self):
        self.printStatus("Going reverse")
        self.writeRegisterSafe(self.inputRegister, 2**self.reverseBitInput)

    def startOperation(self, operationNumber):
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.printStatus("Starting operation " + str(operationNumber))
        self.writeToInputRegister(2**self.startBitInput | operationNumber)
        self.waitFor()

    def stopMoving(self):
        self.writeToInputRegister(2**self.stopBitInput)
        time.sleep(self.standardWaitTime)
        self.writeToInputRegister(0)

    def writeOperationPosition(self, operationPosition, operationNumber):
        if operationPosition > 2**16 or operationPosition < 0:
            raise ValueError("Invalid value for operation position!")
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeRegisterSafe(self.operationPositionLowerRegisters[operationNumber],
                operationPosition)
        time.sleep(self.standardWaitTime)

    def writeOperationSpeed(self, operationSpeed, operationNumber):
        if operationSpeed > 2**16 or operationSpeed < 0:
            raise ValueError("Invalid value for operation speed!")
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeRegisterSafe(self.operationSpeedLowerRegisters[operationNumber],
                operationSpeed)
        time.sleep(self.standardWaitTime)

    def writeOperationMode(self, operationMode, operationNumber):
        if operationMode != 0 and operationMode != 1:
            raise ValueError("Invalid value for operation mode!")
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeRegisterSafe(self.operationModeRegisters[operationNumber],
                operationMode)
        time.sleep(self.standardWaitTime)
