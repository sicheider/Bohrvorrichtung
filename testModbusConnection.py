import stepperMotor

class FakeMaster(object):
    def __init__(self):
        self.isInterrupted = False

    def onInterrupt(self):
        pass

fm = FakeMaster()
rotor = stepperMotor.StepperMotor("rotor", 5, fm)
print("Upper Register:")
print(rotor.readRegisterSafe(1026))
print("Lower Register:")
print(rotor.readRegisterSafe(1027))
