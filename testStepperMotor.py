import stepperMotor

s = stepperMotor.StepperMotor("rotor", 5)
raw_input("writeregister")
s.writeRegisterSafe(127, 65530)
raw_input("readregister")
print s.readRegisterSafe(125)
raw_input("waitfor")
s.waitFor()
s.writeRegisterSafe(127, 65530)
raw_input("startoperation")
s.startOperation(2)
s.writeRegisterSafe(127, 65530)
raw_input("writeoperation")
s.writeOperationPosition(1000, 0)
raw_input("writespeed")
s.writeOperationSpeed(123, 0)
raw_input("writemode")
s.writeOperationMode(1, 0)
