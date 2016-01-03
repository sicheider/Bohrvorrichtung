#include <ModbusMaster.h>

ModbusMaster rotor(0, 1);
ModbusMaster linear(0, 2);
int goButton = 7;
int readyLed = 12;

void writeRegisterRotor(ModbusMaster device, uint16_t adressUpper, uint16_t adressLower, uint16_t valueUpper, uint16_t valueLower)
{
	delay(50);
	device.writeSingleRegister(adressUpper, valueUpper);
	delay(50);
	device.writeSingleRegister(adressLower, valueLower);
	delay(50);
}

/*
main process registers
property		unit			initial value		upper		lower
position		steps			0					1024		1025
speed			Hz				1000				1152		1153
mode			inc(0)/abs(1)	0					1280		1281
function		0-4				0					1408		1409
acceleration	s/kHz			1000				1536		1537
deceleration	s/kHz			1000				1664		1665
current			%%				200					1792		1793
sequential		0/1				0					1920		1921
dwelltime		unknown			0					2048		2049
*/

void setup()
{
	rotor.begin(9600);
	linear.begin(9600);
	pinMode(goButton, INPUT);
	pinMode(readyLed, OUTPUT);
	delay(5000);
	//set rotor positioningsteps
	writeRegisterRotor(rotor, 1024, 1025, 0, 1500);
}

void loop()
{
	digitalWrite(readyLed, HIGH);
	if(digitalRead(goButton) == HIGH)
	{
		digitalWrite(readyLed, LOW);
		rotor.writeSingleRegister(125, 8);
		delay(5000);
	}
}
