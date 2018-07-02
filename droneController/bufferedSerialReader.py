import json
        
class BufferedSerialReader():
    def __init__(self,port,splitChar):
        self.__port = port
        self.__splitChar = splitChar
        self.__setuped = False
        self.__running = False
        self.__sensorLoop = Thread(target=self.run);
        
    def setup(self):
        port = self.getPort()
        print "Opening Port \"%s\"" % port
        if port[:3].upper() == "COM":
            _port = int(port[3:]) - 1
        else:
            _port = port
        
        serPort = serial.Serial(_port, 115200, timeout=.5)
        if not serPort.isOpen():
            raise IOError("Failed to open serial port")
        else:
            self.__setuped = True;
            self.getSensorLoop().start()
    
    def getValue(self):
        pass
    
    def run(self):
        if self.__setuped:
            while self.__running:
                pass
    def getSensorLoop(self):
        return self.__sensorLoop
        
    def getPort(self):
        return self.__port
        
    def getSplitChar(self):
        return self.__splitChar
        
    def setPort(self,port):
        self.__port = port
        
    def setSplitChar(self,splitChar):
        self.__splitChar = splitChar
        
    
