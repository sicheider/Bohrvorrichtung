#ifndef IOControl_h
#define IOControl_h

#include "Arduino.h"

class Device{
	private:
		//Device input pins
		uint8_t start;
		uint8_t m0;
		uint8_t m1;
		uint8_t m2;
		uint8_t fwd;
		uint8_t rvs;
		uint8_t home;
		uint8_t stop;

		//Device output pins
		uint8_t move;

		//sets m0, m1, m2
		void setOperationNoPins(uint8_t operationNo);
		//waits for device to finish operation using move
		void waitFor();
		//sets start pin
		void start();

	public:
		Device(uint8_t _start, uint8_t _m0, uint8_t _m1, uint8_t _m2,
				uint8_t fwd, uint8_t rvs, uint8_t home, uint8_t stop, uint8_t move);
		//start operation and wait for its finish
		void startOperation(uint8_t operationNo);
		//starts home operation and wait for its finish
		void goHome();
};

#endif
