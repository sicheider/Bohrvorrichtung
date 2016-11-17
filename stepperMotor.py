import minimalmodbus
import time
import serial
import logging

class StepperMotor(minimalmodbus.Instrument, object):
    """An Oriental Motor stepper motor. This class uses minimalmodbus to
    communicate over Modbus/RS-485 with the motor.

    .. note::
        Oriental Motors uses upper and lower registers (each 16 bit). Only lower registers are
        supported in this class. If you have to store values greater than 2**16 you have to use
        upper registers too.

    Attributes:
        * baudrate: The baudrate of the serial communication
        * stopbits: Stopbit configuration of the serial communication
        * parity: Parity configuration of the serial communication
        * timeout: Modbus timeout
        * waitForPingTime: Time between pings to the motor to check if its still moving
        * standardWaitTime: Time to wait after each modbus communication
        * maxFailCounter: If a communication failes maxFailCounter times a exception is raised
        * master: An instance of the class which is controlling the motor. Must have an attribute named
        "isInterrupted" and a method named "handleInterrupt"
        * registers: See oriental motor documentation
    """
    def __init__(self, name, adress, master,
            serialPort = "/dev/ttyUSB0",
            baudrate = 19200,
            stopbits = 1,
            parity = serial.PARITY_NONE,
            timeout = 0.05,
            standardWaitTime = 0.02,
            waitForPingTime = 0.2,
            maxFailCounter = 50):
        """Contructor. Initializes everything. See Attributes.

        Args:
            * name: The stepper motor name
            * adress: The modbus adress of the motor
            * serialport: The usb serial port which the motor is attached to
            * rest: See class Attributes

        Returns:
            None

        Raises:
            None
        """
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
        """
        Args:
            * message: The massage to wrap

        Returns:
            A wrapped string containing name and message

        Raises:
            None
        """
        return ("[" + self.name + "] " + message)

    def getBitFromRegister(self, adress, bit):
        """Reads a bit from a register.

        Args:
            * adress (int): Register adress
            * bit (int): Number of the bit

        Returns:
            True or False

        Raises:
            None
        """
        registerValue = self.readRegisterSafe(adress)
        if registerValue & 2**bit == 0:
            return False
        return True

    def writeRegisterSafe(self, adress, value):
        """Writes a value to a register making sure the communication was successfull.
        Raises an exception if the communication failes maxFailCounter times.

        Args:
            * adress (int): The adress to write to
            * value (int): The value to write

        Returns:
            None

        Raises:
            IOError
        """
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
        """Reads a value from a register making sure the communication was successfull.
        Raises an exception if the communication failes maxFailCounter times.

        Args:
            * adress (int): The adress to from 

        Returns:
            None

        Raises:
            IOError
        """
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
        """Waits for the motor to finish the operation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
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
        """Writes a value to the input register and resets it.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.writeRegisterSafe(self.inputRegister, value)
        time.sleep(self.standardWaitTime)
        self.writeRegisterSafe(self.inputRegister, 0)
        time.sleep(self.standardWaitTime)

    def goHome(self):
        """Drives the motor to home position.
        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.printStatus("Going home")
        self.writeToInputRegister(2**self.homeBitInput)
        self.waitFor()

    def goForward(self):
        """Starts forward moving of the motor.
        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.printStatus("Going forward")
        self.writeRegisterSafe(self.inputRegister, 2**self.forwardBitInput)

    def goReverse(self):
        """Starts reverse moving of the motor.
        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.printStatus("Going reverse")
        self.writeRegisterSafe(self.inputRegister, 2**self.reverseBitInput)

    def startOperation(self, operationNumber):
        """Starts a operation which is stored in the operation registers.

        Args:
            * operationNumber (int): The operation number to start

        Returns:
            None

        Raises:
            ValueError if the operation number is invalid
        """
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.printStatus("Starting operation " + str(operationNumber))
        self.writeToInputRegister(2**self.startBitInput | operationNumber)
        self.waitFor()

    def stopMoving(self):
        """Stops the motor.
        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.writeToInputRegister(2**self.stopBitInput)
        time.sleep(self.standardWaitTime)
        self.writeToInputRegister(0)

    def writeOperationPosition(self, operationPosition, operationNumber):
        """Writes the operation position for a operation number.

        Args:
            * operationPosition (int): The steps to move for the operation number
            * operationNumber (int)

        Returns:
            None

        Raises:
            ValueError
        """
        if operationPosition > 2**16 or operationPosition < 0:
            raise ValueError("Invalid value for operation position!")
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeRegisterSafe(self.operationPositionLowerRegisters[operationNumber],
                operationPosition)
        time.sleep(self.standardWaitTime)

    def writeOperationSpeed(self, operationSpeed, operationNumber):
        """Writes the operation speed for a operation number.

        Args:
            * operationSpeed (int): The speed in Hz the operation is performed
            * operationNumber (int)

        Returns:
            None

        Raises:
            ValueError
        """
        if operationSpeed > 2**16 or operationSpeed < 0:
            raise ValueError("Invalid value for operation speed!")
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeRegisterSafe(self.operationSpeedLowerRegisters[operationNumber],
                operationSpeed)
        time.sleep(self.standardWaitTime)

    def writeOperationMode(self, operationMode, operationNumber):
        """Writes the operation mode for a operation number.

        Args:
            * operationMode (0|1): The operation mode for the operation. 0 for incremental,
            1 for absolute
            * operationNumber (int)

        Returns:
            None

        Raises:
            ValueError
        """
        if operationMode != 0 and operationMode != 1:
            raise ValueError("Invalid value for operation mode!")
        if operationNumber > self.operationCount or operationNumber < 0:
            raise ValueError("Invalid value for operation number!")
        self.writeRegisterSafe(self.operationModeRegisters[operationNumber],
                operationMode)
        time.sleep(self.standardWaitTime)
