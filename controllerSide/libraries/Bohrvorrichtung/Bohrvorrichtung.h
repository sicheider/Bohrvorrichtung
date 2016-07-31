#ifndef Bohrvorrichtung_h
#define Bohrvorrichtung_h

#include "Arduino.h"
#include "ModbusMaster.h"

class Device : public ModbusMaster{
	private:
		String name;
		uint8_t adress;
		uint16_t transmitData;
		static const uint16_t outputRegister = 0x007F;
		static const uint16_t inputRegister = 0x007D;
		static const uint8_t inputStartBit = 3;
		static const uint8_t inputHomeBit = 4;
		static const uint8_t outputReadyBit = 5;
		static const uint8_t mSignalStartBit = 0;
		static const uint8_t mSignalCount = 3;

		void waitFor();
		void setFlag();
		void unsetFlag();
		void setOperationNo(uint16_t);
		void printStatus(String);

	public:
		void startOperation(uint16_t);
		void goHome();
		Device(String, uint8_t, uint8_t, uint16_t);
};

#endif
