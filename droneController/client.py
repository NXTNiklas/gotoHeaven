#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import uuid
import errno
import os

sys.path.insert(0,'/home/pi/code/websocket/websocket')

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from loggingManager.LoggingManager import LoggingManager




class Client(object):
    def __init__(self, url, timeout):
        self.__initLog()
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect(self.__log)
        self.ioloop.start()

    def __initLog(self):
        try:
            self.__log
        except AttributeError:
            try:
                self.uuid = str(uuid.uuid4())
                #Try to create Loggingpath:
                logpath = os.path.dirname(os.path.realpath(__file__))+'/logs/Client/'
                os.makedirs(logpath,0750 )
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            
            self.__log = LoggingManager(10,logpath+self.uuid+'.log',self.uuid)
            self.__log.info('Log Succesfully Created!')

    @gen.coroutine
    def connect(self,log):
        log.info("trying to connect")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            log.exception("connection error")
        else:
            log.info("connected")
            self.run(log)

    @gen.coroutine
    def run(self,log):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                log.critical("connection closed")
                self.ws = None
                break
            else:
                log.info(msg)
                

if __name__ == "__main__":
      
    client = Client("ws://localhost:8888/ws/drone", 5)