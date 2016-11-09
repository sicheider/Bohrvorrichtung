import stepperMotor

rotor = stepperMotor.StepperMotor("rotor", "/dev/ttyUSB0", 5)
linear = stepperMotor.StepperMotor("linear", "/dev/ttyUSB0", 6)
linear.goHome()
linear.writeOperationPosition(15000, 0)
linear.writeOperationPosition(16100, 1)
linear.writeOperationPosition(15000, 2)
linear.writeOperationSpeed(15000, 0)
linear.writeOperationSpeed(125, 1)
linear.writeOperationSpeed(2000, 2)
linear.writeOperationMode(1, 0)
linear.writeOperationMode(1, 1)
linear.writeOperationMode(1, 2)

while True:
    raw_input("Zum Starten ENTER druecken...")
    rotor.goHome()
    linear.startOperation(0)
    for _ in range(0, 32):
        linear.startOperation(1)
        linear.startOperation(2)
        rotor.startOperation(0)
    linear.goHome()
