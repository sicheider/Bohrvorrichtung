#include <ModbusMaster.h>

ModbusMaster rotor(0, 1);
ModbusMaster linear(0, 2);

void writeRegisterRotor(uint16_t adressUpper, uint16_t adressLower, uint16_t valueUpper, uint16_t valueLower)
{
	delay(50);
	rotor.writeSingleRegister(adressUpper, valueUpper);
	delay(50);
	rotor.writeSingleRegister(adressLower, valueLower);
	delay(50);
}

void setup()
{
	rotor.begin(9600);
	linear.begin(9600);
	delay(5000);
	//set rotor positioningsteps
	writeRegisterRotor(1024, 1025, 0, 500);
	/*
	//set rotor operationspeed
	writeRegisterRotor(1152, 1153, 0, 2);
	//set rotor operationmode
	writeRegisterRotor(1280, 1281, 0, 0);
	//set rotor operationfunction
	writeRegisterRotor(1408, 1409, 0, 0);
	//set rotor acceleration/deceleration unit
	writeRegisterRotor(654, 655, 0, 1);
	//set rotor acceleration
	writeRegisterRotor(1536, 1537, 0, 1000);
	//set rotor deceleration
	writeRegisterRotor(1664, 1665, 0, 1000);
	//set rotor pushcurrent
	writeRegisterRotor(1792, 1793, 0, 200);
	//set rotor sequential positioning
	writeRegisterRotor(1920, 1921, 0, 0);
	//set rotor dwelltime
	writeRegisterRotor(2048, 2049, 0, 0);
	*/
}

void loop()
{
	rotor.writeSingleRegister(125, 8);
	delay(5000);
}
