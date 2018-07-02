import logging, inspect

# Level of Logging:
# CRITICAL  50
# ERROR	    40
# WARNING	30
# INFO	    20
# DEBUG	    10
# NOTSET	0

class LoggingManager:
    def __init__(self,logLevel,pathToLog,logName):
        logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(logName)
        self.log.setLevel(logLevel) 
        
        formatter = logging.Formatter("{time: %(asctime)s ;uuid:%(name)s; loglevel: %(levelname)s; message: %(message)s}")
        # Setup file logging as well
        fh = logging.FileHandler(pathToLog,mode='a')
        fh.setLevel(logLevel)
        fh.setFormatter(formatter)
        self.log.addHandler(fh)
        
        
    def debug(self,message):
        self.logMessage(message,10)
        
    def info(self,message):
        self.logMessage(message,20)
    
    def warning(self,message):
        self.logMessage(message,30)
        
    def error(self,message):
        self.logMessage(message,40)
        
    def critical(self,message):
        self.logMessage(message,50)
           
    def exception(self,message):
        self.logMessage(message,40)
    
    def logMessage(self,message,level):        
        func = inspect.currentframe().f_back.f_back.f_code
        str = ("%s; method: %s; file: %s ;line :%i;" % (message, func.co_name, func.co_filename, func.co_firstlineno))
        self.log.log(level,str)