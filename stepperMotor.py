import minimalmodbus
import time
import serial

class StepperMotor(minimalmodbus.Instrument, object):
    def __init__(self, name, serialPort, adress):
        #minimalmodbus.BAUDRATE = 19200
        #minimalmodbus.STOPBITS = 1
        #minimalmodbus.PARITY = serial.PARITY_NONE
        #minimalmodbus.TIMEOUT = 0.05
        super(StepperMotor, self).__init__(serialPort, adress)
        self.waitForPingTime = 0.1
        self.standardWaitTime = 0.02

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

    def printStatus(self, message):
        print("[" + self.name + "] " + message)

    def getBitFromRegister(self, adress, bit):
        registerValue = self.readRegisterSafe(adress)
        if registerValue & 2**bit == 0:
            return False
        return True

    def writeRegisterSafe(self, adress, value):
        run = True
        while run:
            try:
                super(StepperMotor, self).write_register(adress, value)
                run = False
            except IOError:
                self.printStatus("IOError while writing register")
                time.sleep(self.standardWaitTime)
            except ValueError as e:
                self.printStatus("ValueError while writing register")
                self.printStatus(e.message)
                time.sleep(self.standardWaitTime)

    def readRegisterSafe(self, adress):
        run = True
        while run:
            try:
                return super(StepperMotor, self).read_register(adress)
            except IOError:
                self.printStatus("IOError while reading from register")
                time.sleep(self.standardWaitTime)
            except ValueError as e:
                self.printStatus("ValueError while reading from register")
                self.printStatus(e.message)
                time.sleep(self.standardWaitTime)

    def waitFor(self):
        self.printStatus("Waiting for operation to finish")
        run = True
        while run:
            move = self.getBitFromRegister(self.outputRegister, self.moveBitOutput)
            if not move:
                run = False
            time.sleep(self.waitForPingTime)
        self.printStatus("Operation finished")
        time.sleep(self.standardWaitTime)

    def writeToInputRegister(self, value):
        self.writeRegisterSafe(self.inputRegister, value)
        time.sleep(self.standardWaitTime)
        self.writeRegisterSafe(self.inputRegister, 0)
        time.sleep(self.standardWaitTime)

    def goHome(self):
        self.writeToInputRegister(2**self.homeBitInput)
        self.waitFor()

    def goForward(self):
        self.writeRegisterSafe(self.inputRegister, 2**self.forwardBitInput)

    def goReverse(self):
        self.writeRegisterSafe(self.inputRegister, 2**self.reverseBitInput)

    def startOperation(self, operationNumber):
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeToInputRegister(2**self.startBitInput | operationNumber)
        self.waitFor()

    def stopMoving(self):
        self.writeToInputRegister(2**self.stopBitInput)

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
