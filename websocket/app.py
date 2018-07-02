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
from LoggingManager import LoggingManager
from tornado.ioloop import PeriodicCallback

class drones():
    def __init__(self):
        self.__drones = []
        
    def __getdrones(self):
        return self.__drones
    
    def append(self,droneHandler):
        if self not in self.__getdrones():
            self.__getdrones().append(droneHandler)
            self.printNewdrone(droneHandler)
    
    def remove(self,droneHandler):
        if droneHandler in self.__getdrones():
            self.__getdrones().remove(droneHandler)
            self.printRemovedrone(droneHandler)
            
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
        print(droneJSON)
        for c in clients:
            c.write_message(json.dumps(droneJSON))
        for drone in self.__getdrones():
            drone.sendMyData()    
            
    def printNewdrone(self,dronehandler):
        data = {
                  'droneID':dronehandler.id
                , 'name':dronehandler.name
                , 'uuid':dronehandler.uuid
                , 'action': 'add'
            }
        for c in clients:
            c.write_message(json.dumps(data))
            
    def printRemovedrone(self,dronehandler):
        data = {
                  'droneID':dronehandler.id
                , 'name':dronehandler.name
                , 'uuid':dronehandler.uuid
                , 'action': 'remove'
            }
        for c in clients:
            c.write_message(json.dumps(data))
    
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
        if client in clients:
            client.write_message(json.dumps(droneJSON))
        for drone in self.__getdrones():
            drone.sendMyData()        
            
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
                
        if self not in clients:
            clients.append(self)
        
        drones.printdronesToClient(self);
            
    def on_close(self):
        if self in clients:
            clients.remove(self)
            
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
            except KeyError:
                data = {'error': 'Nothing to do...','errorMessage': 'No Action defined'}
                print(json.dumps(data))
                self.write_message(json.dumps(data))
            else:
                if action == 'refresh':
                    #Checking if fields are set
                    try:
                        uuid = messageJSON['uuid']
                    except KeyError:
                        data = {'error': 'Who should i refresh?','errorMessage': 'No uuid defined'}
                        print(json.dumps(data))
                        self.write_message(json.dumps(data))
                    else:
                        drones.refresh(self,uuid)
        
            
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
                logpath = os.path.dirname(os.path.realpath(__file__))+'/logs/Logins/'
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
            data = {'error': 'I don\'t understand you! Speak JSON!'}
            self.__log.exception(data)
            self.write_message(json.dumps(data))
        else:
            try:
                action = messageJSON['action']
            except KeyError:
                try:
                    error = messageJSON['error']
                except KeyError:
                    data = {'error': 'Nothing to do...'}
                    self.__log.exception(data)
                    self.write_message(json.dumps(data))
                else:
                    self.__log.error(error)
            else:
                data = {'error': 'unknown Action'}
                self.__log.exception(data)
                self.write_message(json.dumps(data))
                    
    def sendMyData(self):
        try:
            data = {
                'action': 'changeData'
              , 'uuid': self.uuid
            }
            self.__log.debug('\'Sending Data\': '+ json.dumps(data))
            for c in clients:
                c.write_message(json.dumps(data))
        except AttributeError:
            pass
            
    def refresh(self):
        data = {'action':'refresh'}
        self.__log.info(data)
        self.write_message(data)
    
app = web.Application([
    (r'/', IndexHandler),
    (r'/droneSym', Index2Handler),
    (r'/ws/view', ViewHandler),
    (r'/ws/drone', Drone),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
], websocket_ping_interval = 10, websocket_ping_timeout = 20)

clients = []
drones = drones()

if __name__ == '__main__':
    #ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_ctx.load_cert_chain("/etc/apache2/ssl.crt/bpw.de.crt",
    #               "/etc/apache2/ssl.key/bpw.de.key")
    server = httpserver.HTTPServer(app)
    server.listen(8888)
    ioloop.IOLoop.instance().start()
