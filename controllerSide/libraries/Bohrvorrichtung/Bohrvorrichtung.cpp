#include "Arduino.h"
#include "ModbusMaster.h"
#include "Bohrvorrichtung.h"

Device::Device(uint8_t adress, uint8_t serialPort, uint16_t baudRate) 
: ModbusMaster(serialPort, adress){
	begin(baudRate);
}

void Device::setStartFlag(){
	transmitData = (uint16_t)pow(2, inputStartBit) | transmitData;
}

void Device::unsetStartFlag(){
	transmitData = (uint16_t)pow(2, inputStartBit) ^ transmitData;
}

void Device::waitFor(){
	uint16_t result;
	do{
		clearResponseBuffer();
		readHoldingRegisters(outputRegister, 1);
		result = getResponseBuffer(0);
		delay(100);
	}while((result & (uint16_t)pow(2, outputReadyBit)) != (uint16_t)pow(2, outputReadyBit));
}

void Device::setOperationNo(uint16_t operationNo){
	transmitData = 0;
	for(int i = mSignalStartBit; i < mSignalCount; i++){
		if((operationNo & (uint16_t)pow(2, i)) == (uint16_t)pow(2, i)){
			transmitData = transmitData | (uint16_t)pow(2, i);
		}
	}
}

void Device::startOperation(uint16_t operationNo){
	setOperationNo(operationNo);
	setStartFlag();
	writeSingleRegister(inputRegister, transmitData);
	delay(20);
	unsetStartFlag();
	writeSingleRegister(inputRegister, transmitData);
	waitFor();
}

void Device::goHome(){
	transmitData = 0;
	transmitData = transmitData | (uint16_t)pow(2, inputHomeBit);
	writeSingleRegister(inputRegister, transmitData);
	delay(20);
	transmitData = 0;
	writeSingleRegister(inputRegister, transmitData);
	waitFor();
}
