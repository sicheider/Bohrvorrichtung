#include "Arduino.h"
#include "ModbusMaster.h"
#include "Bohrvorrichtung.h"

Device::Device(String _name, uint8_t adress, uint8_t serialPort, uint16_t baudRate) 
: ModbusMaster(serialPort, adress){
	begin(baudRate);
	name = _name;
}

void Device::setFlag(uint8_t bit){
	uint16_t operand = 1 << bit;
	transmitData = operand | transmitData;
}

void Device::unsetFlag(uint8_t bit){
	uint16_t operand = 1 << bit;
	transmitData = operand ^ transmitData;
}

void Device::printStatus(String status){
	String result = name + ": " + status;
	Serial.println(result);
}

void Device::waitFor(){
	printStatus("Waiting...");
	uint16_t operand = 1 << outputReadyBit;
	uint16_t result;
	delay(20);
	do{
		clearResponseBuffer();
		readHoldingRegisters(outputRegister, 1);
		result = getResponseBuffer(0);
		delay(100);
	}while((result & operand) != operand);
	printStatus("Ready!");
}

void Device::setOperationNo(uint16_t operationNo){
	transmitData = 0;
	uint16_t operand;
	for(int i = mSignalStartBit; i < mSignalCount; i++){
		operand = 1 << i;
		if(((operationNo << mSignalStartBit) & operand) == operand){
			transmitData = transmitData | operand;
		}
	}
}

void Device::startOperation(uint16_t operationNo){
	printStatus("Operating...");
	setOperationNo(operationNo);
	setFlag(inputStartBit);
	writeSingleRegister(inputRegister, transmitData);
	delay(20);
	unsetFlag(inputStartBit);
	writeSingleRegister(inputRegister, transmitData);
	waitFor();
}

void Device::goHome(){
	printStatus("Going home...");
	transmitData = 0;
	setFlag(inputHomeBit);
	writeSingleRegister(inputRegister, transmitData);
	delay(20);
	unsetFlag(inputHomeBit);
	writeSingleRegister(inputRegister, transmitData);
	waitFor();
}
