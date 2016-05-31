#include "IOControl.h"
#include "Arduino.h"

Device::Device(uint8_t _start, uint8_t _m0, uint8_t _m1, uint8_t _m2,
		uint8_t _fwd, uint8_t _rvs, uint8_t _home, uint8_t _stop, uint8_t _move){
	start = _start;
	m0 = _m0;
	m1 = _m1;
	m2 = _m2;
	fwd = _fwd;
	rvs = _rvs;
	home = _home;
	stop = _stop;
	move = _move;
	pinMode(start, OUTPUT);
	pinMode(m0, OUTPUT);
	pinMode(m1, OUTPUT);
	pinMode(m2, OUTPUT);
	pinMode(fwd, OUTPUT);
	pinMode(rvs, OUTPUT);
	pinMode(home, OUTPUT);
	pinMode(stop, OUTPUT);
	pinMode(move, INPUT);
}

void Device::setOperationNoPins(uint8_t operationNo){
	if(operationNo <= 7){
		if(operationNo & 1 == 1){
			digitalWrite(m0, HIGH);
		}
		else{
			digitalWrite(m0, LOW);
		}
		if(operationNo & 2 == 2){
			digitalWrite(m1, HIGH);
		}
		else{
			digitalWrite(m1, LOW);
		}
		if(operationNo & 4 == 4){
			digitalWrite(m2, HIGH);
		}
		else{
			digitalWrite(m2, LOW);
		}
	}
	delay(20);
}

void Device::waitFor(){
	while(digitalRead(move) == HIGH){
	}
	delay(20);
}

void Device::start(){
	digitalWrite(start, HIGH);
	delay(20);
	digitalWrite(start, LOW);
}
	
void Device::startOperation(uint8_t operationNo){
	setOperationNoPins(operationNo);
	start();
	waitFor();
}

void Device::goHome(){
	digitalWrite(home, HIGH);
	delay(50);
	digitalWrite(home, LOW);
	waitFor();
}
