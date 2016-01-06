"""
Class to write a ProcessData file
filestructure:

    initBlock
    -
    sequenceBlock

structure initBlock:

    slaveadress, adressUpper, adressLower, valueUpper, valueLower
    with:
        slaveadress = 1 -> rotor
        slaveadress = 2 -> linear

structure sequenceBlock:

    slaveadress, processNumber, rotationDirection
    with:
        slaveadress = 1 -> rotor
        slaveadress = 2 -> linear
"""


class ProcessData:
    """Writes a ProcessData file"""
    def __init__(self):
        self.fileName = 'ProcessData.txt'
        self.whitespaceCharacter = ' '
        self.lineEndCharacter = '\n'
        try:
            self.fileObject = open(self.fileName, 'w')
        except:
            pass
        pass

    def writeInitBlock(self, initList):
        for i in initList:
            self.fileObject.write(str(i[0]) + self.whitespaceCharacter +
                                  str(i[1]) + self.whitespaceCharacter +
                                  str(i[2]) + self.whitespaceCharacter +
                                  str(i[3]) + self.whitespaceCharacter +
                                  str(i[4]) + self.lineEndCharacter)
        self.fileObject.write('-\n')
        pass

    def writeSequenceBlock(self, sequenceList):
        for i in sequenceList:
            self.fileObject.write(str(i[0]) + self.whitespaceCharacter +
                                  str(i[1]) + self.whitespaceCharacter +
                                  str(i[2]) + self.lineEndCharacter)
        pass

    def writeProcessData(self, initList, sequenceList):
        self.writeInitBlock(initList)
        self.writeSequenceBlock(sequenceList)
        self.fileObject.close()
        pass
