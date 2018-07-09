from tornado import websocket, web, ioloop, httpserver
import json
import ssl
from urllib import urlencode
from urllib2 import urlopen, Request
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse
import uuid
from base64 import decodestring
from datetime import datetime
import os
import errno
from tornado.ioloop import PeriodicCallback
from loggingManager.LoggingManager import LoggingManager

def initGlobalLog():
    try:
        loguuid = str(uuid.uuid4())
        #Try to create Loggingpath:
        logpath = os.path.dirname(os.path.realpath(__file__))+'/loggingManager/logs/GlobalView/'
        os.makedirs(logpath,0750 )
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    logger = LoggingManager(0,logpath+loguuid+'.log',loguuid,drones)
    logger.info('Log Succesfully Created!')
    return logger
            

class drones():
    def __init__(self):
        self.__drones = []
        self.__views = []
        
    def __getdrones(self):
        return self.__drones
    def __getViews(self):
        return self.__views
        
    def append(self,droneHandler):
        if self not in self.__getdrones():
            self.__getdrones().append(droneHandler)
            self.printNewdrone(droneHandler)
    
    def remove(self,droneHandler):
        if droneHandler in self.__getdrones():
            self.__getdrones().remove(droneHandler)
            self.printRemovedrone(droneHandler)
        
    def appendView(self,viewHandler):
        if self not in self.__getViews():
            self.__getViews().append(viewHandler)
    
    def removeView(self,viewHandler):
        if viewHandler in self.__getViews():
            self.__getViews().remove(viewHandler)
            
    def printdronesToAll(self):
        droneJSON = {}
        droneJSON['drones'] = [];
        for droneHandler in self.__getdrones():
            data = {
                  'droneID':droneHandler.id
                , 'name':droneHandler.name
                , 'uuid':droneHandler.uuid
            }
            droneJSON['drones'].append(data)
        droneJSON['action'] = 'printAll'    
        
        self.sendToViewClients(json.dumps(droneJSON))            
            
    def printNewdrone(self,dronehandler):
        data = {
                  'droneID':dronehandler.id
                , 'name':dronehandler.name
                , 'uuid':dronehandler.uuid
                , 'action': 'add'
            }
        self.sendToViewClients(json.dumps(data))
            
    def printRemovedrone(self,dronehandler):
        data = {
                  'droneID':dronehandler.id
                , 'name':dronehandler.name
                , 'uuid':dronehandler.uuid
                , 'action': 'remove'
            }
        self.sendToViewClients(json.dumps(data))
    
    def printdronesToClient(self,client):
        droneJSON = {}
        droneJSON['drones'] = [];
        for drone in self.__getdrones():
            data = {
                  'droneID':drone.id
                , 'name':drone.name
                , 'uuid':drone.uuid
            }
            droneJSON['drones'].append(data)
        droneJSON['action'] = 'printAll';    
        print(droneJSON)
        self.sendToViewClients(json.dumps(droneJSON))
        
            
    def isOpen(self,drone):
        if drone in self.__getdrones():
            return True
        else:
            return False
    
    def refresh(self,c,uuid):
        found = False;
        for drone in self.__getdrones():
            if drone.uuid == uuid:
                result = drone.refresh()
                found = True
        if found is False:
            data = {'error': 'Unkown ID','errorMessage': 'ID doesn\'t exists!','uuid': uuid}
            print(json.dumps(data))
            c.write_message(json.dumps(data))
        else:
            data = {'action':'log', 'message': 'Aktualisierungsanfrage verarbeitet!'}
            print(json.dumps(data))
            c.write_message(json.dumps(data))
            
    def send(self,message):
        for drone in self.__getdrones():
            drone.send(message)
    
    def sendToViewClients(self,message):
        for view in self.__getViews():
            view.send(message)

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class Index2Handler(web.RequestHandler):
    def get(self):
        self.render("index2.html")

class ViewHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self, *args):
        drones.appendView(self)
        drones.printdronesToClient(self);
            
    def on_close(self):
        drones.removeView(self)
        
    def on_message(self,message):
        try:
            messageJSON = json.loads(message)
        except ValueError:
            data = {'error': 'I don\'t understand you! Speak JSON!'}
            print(json.dumps(data))
            self.write_message(json.dumps(data))
        else:
            try:
                action = messageJSON['action']
                param = messageJSON['params'];
            except KeyError:
                data = {'error': 'Nothing to do...','errorMessage': 'No Action defined'}
                print(json.dumps(data))
                self.write_message(json.dumps(data))
            else:
                if action == 'refresh':
                    #Checking if fields are set
                    try:
                        uuid = param[0]
                    except KeyError:
                        data = {'error': 'Who should i refresh?','errorMessage': 'No uuid defined'}
                        print(json.dumps(data))
                        self.write_message(json.dumps(data))
                    else:
                        drones.refresh(self,uuid)
                else:
                    globalViewLogger.info(messageJSON)
                    drones.send(json.dumps(messageJSON))
    def send(self,message):
        self.write_message(json.dumps(message))
        
class Drone(websocket.WebSocketHandler):
    def check_origin(self, origin):
        self.__initLog();
        return True
    
    def __initLog(self):
        try:
            self.__log
        except AttributeError:
            try:
                self.uuid = str(uuid.uuid4())
                #Try to create Loggingpath:
                logpath = os.path.dirname(os.path.realpath(__file__))+'/loggingManager/logs/Logins/'
                os.makedirs(logpath,0750 )
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            
            self.__log = LoggingManager(10,logpath+self.uuid+'.log',self.uuid)
            self.__log.info('Log Succesfully Created!')
            
    def open(self, *args):
        self.__initLog();
        self.id = 1337
        self.name = 'KillerDrone'
        if not drones.isOpen(self):
            drones.append(self)
        
    def on_close(self):
        self.__log.info('Websocketconnection closed!')
        if drones.isOpen(self):
            drones.remove(self)
            
    def on_message(self,message):
        self.__log.info('Recieved message: '+message)
        try:
            messageJSON = json.loads(message)
        except ValueError:
            data = {'action':'error'
            ,'error': 'I don\'t understand you! Speak JSON!'}
            self.__log.exception(data)
            self.write_message(json.dumps(data))
        else:
            try:
                action = messageJSON['action']
            except KeyError:
                try:
                    error = messageJSON['error']
                except KeyError:
                    data = {'action':'error','error': 'Nothing to do...'}
                    self.__log.exception(data)
                    self.write_message(json.dumps(data))
                else:
                    self.__log.error(error)
            else:
                data = {'action':'error','error': 'unknown Action'}
                self.__log.exception(data)
                self.write_message(json.dumps(data))
            
    def refresh(self):
        data = {'action':'refresh'}
        self.__log.info(data)
        self.write_message(data)
    
    def send(self,message):
        self.__log.info(message)
        self.write_message(message)
    
app = web.Application([
    (r'/', IndexHandler),
    (r'/droneSym', Index2Handler),
    (r'/ws/view', ViewHandler),
    (r'/ws/drone', Drone),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
], websocket_ping_interval = 10, websocket_ping_timeout = 20)

drones = drones()
globalViewLogger = initGlobalLog()

if __name__ == '__main__':
    #ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_ctx.load_cert_chain("/etc/apache2/ssl.crt/bpw.de.crt",
    #               "/etc/apache2/ssl.key/bpw.de.key")
    server = httpserver.HTTPServer(app)
    server.listen(8888)
    ioloop.IOLoop.instance().start()
