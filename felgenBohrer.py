import stepperMotor

rotor = stepperMotor.StepperMotor("rotor", "/dev/ttyUSB0", 5)
linear = stepperMotor.StepperMotor("linear", "/dev/ttyUSB0", 6)
while True:
    raw_input("Zum Starten ENTER druecken...")
    rotor.goHome()
    linear.goHome()
    linear.startOperation(0)
    for _ in range(0, 32):
        linear.startOperation(1)
        linear.startOperation(2)
        rotor.startOperation(0)
