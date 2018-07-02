clients = dict()

class WebServer(object):
    def __init__(self, port=8080):

        define("port", default=port, help="Run on the given port", type=int)

        app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/(?P<Id>\w*)', MyWebSocketHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':'static/'}),
        #(r'/ws', MyWebSocketHandler),
        ])

        print("Trailerscan Websocket | Browse to <IP>:"+str(port)+" and have fun!")

        parse_command_line()
        app.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, **kwargs):
        if "Id" in kwargs.keys():
            print "Your client id is: %s" % (kwargs["Id"],)
        self.render("index.html")
        #self.finish()


class MyWebSocketHandler(tornado.websocket.WebSocketHandler):

    def open(self, *args, **kwargs):
        self.id = kwargs["Id"]
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}

    def on_message(self, message):
        print "Client %s received a message: %s" % (self.id, message)
        #self.write_message("Client id: %s" % (list,))


    def on_close(self):
        if self.id in clients:
            del clients[self.id]

    def check_origin(self, origin):
        return True


if __name__ == "__main__":

    server = WebServer()
