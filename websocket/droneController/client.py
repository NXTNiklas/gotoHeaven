#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'/home/pi/code/websocket/websocket')
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from websocket import LoggingManager



class Client(object):
    def __init__(self, url, timeout,logger):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.ioloop.start()
        self.__logger = logger

    @gen.coroutine
    def connect(self):
        logger.info("trying to connect")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print "connection error"
        else:
            print "connected"
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                print "connection closed"
                self.ws = None
                break
            else:
                print(msg)
                

if __name__ == "__main__":
    logger = LoggingManager();
    client = Client("ws://localhost:8888/ws/drone", 5)