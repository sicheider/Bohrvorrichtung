import stepperMotor
import logging

class dummyMaster(object):

    isInterrupted = False

    def __init_(self):
        pass

    def onInterrupt(self):
        pass

m = dummyMaster()
logging.basicConfig(level = logging.DEBUG)
rotor = stepperMotor.StepperMotor("rotor", 5, m, serialPort = "/dev/ttyUSB0")
linear = stepperMotor.StepperMotor("linear", 6, m, serialPort = "/dev/ttyUSB0")
linear.goHome()
rotor.writeOperationPosition(1250, 0)
rotor.writeOperationSpeed(2000, 0)
linear.writeOperationPosition(15000, 0)
linear.writeOperationPosition(16100, 1)
linear.writeOperationPosition(15000, 2)
linear.writeOperationSpeed(15000, 0)
linear.writeOperationSpeed(125, 1)
linear.writeOperationSpeed(2000, 2)
linear.writeOperationMode(1, 0)
linear.writeOperationMode(1, 1)

while True:
    raw_input("Zum Starten ENTER druecken...")
    rotor.goHome()
    linear.startOperation(0)
    for _ in range(0, 32):
        linear.startOperation(1)
        linear.startOperation(2)
        rotor.startOperation(0)
    linear.goHome()
