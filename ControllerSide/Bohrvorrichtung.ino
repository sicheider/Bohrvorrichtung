#include <ModbusMaster.h>

ModbusMaster rotor(1, 1);
ModbusMaster linear(1, 2);
int goButton = 22;
int readyLed = 52;
int dataEnable = 36;
int recieveEnable = 38;
int rotationDirectionLinear = 1;


/*
main process registers
property        unit            initial value       upper       lower
position        steps           0                   1024        1025
speed           Hz              1000                1152        1153
mode            inc(0)/abs(1)   0                   1280        1281
function        0-4             0                   1408        1409
acceleration    s/kHz           1000                1536        1537
deceleration    s/kHz           1000                1664        1665
current         %%              200                 1792        1793
sequential      0/1             0                   1920        1921
dwelltime       unknown         0                   2048        2049
*/

void setup(){
	digitalWrite(readyLed, LOW);
	rotor.begin(19200);
	linear.begin(19200);
  Serial.begin(9600);
	pinMode(goButton, INPUT);
	pinMode(readyLed, OUTPUT);
  pinMode(dataEnable, OUTPUT);
  pinMode(recieveEnable, OUTPUT);
  digitalWrite(dataEnable, HIGH);
  digitalWrite(recieveEnable, HIGH);
	delay(5000);
	//set rotor positioningsteps
	//writeRegister(rotor, 1024, 1025, 0, 1500);
}

void loop(){
  digitalWrite(readyLed, LOW);
	ping(rotor);
}

void writeRegister(ModbusMaster device, uint16_t adressUpper, uint16_t adressLower, uint16_t valueUpper, uint16_t valueLower){
	delay(50);
	device.writeSingleRegister(adressUpper, valueUpper);
	delay(50);
	device.writeSingleRegister(adressLower, valueLower);
	delay(50);
}

uint16_t waitForRequest(ModbusMaster device){
	uint16_t result;
	while(device.getResponseBuffer(0) == 0){
	}
	result = device.getResponseBuffer(0);
	device.clearResponseBuffer();
	delay(50);
	return result;
}

void switchRotationDirectionLinear(){
	if(rotationDirectionLinear == 0){
		writeRegister(linear, 900, 901, 0, 1);
		rotationDirectionLinear = 1;
	}
	else{
		writeRegister(linear, 900, 901, 0, 0);
		rotationDirectionLinear = 0;
	}
}

int ping(ModbusMaster device){
  int result = 0;
  device.clearResponseBuffer();
  device.readHoldingRegisters(500, 64);
  for(int i = 0; i < 64; i++){
    Serial.println(device.getResponseBuffer(i));
  }
  if(device.getResponseBuffer(0) != 0){
    result = 1;
  }
  return result;
}

