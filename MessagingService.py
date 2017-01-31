###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################


import uuid
import sys
import json

from flask import Flask, render_template

from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

users = {}


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            if "heart_beat" not in payload.decode('utf8'):
                print("Debug message received: {0}".format(payload.decode('utf8')))
            # check if it is for subscription

            message_recv_dict = json.loads(payload.decode('utf8'))
            if "subscribe_user_name" in message_recv_dict:
                # add username to users
                user_name_subs = message_recv_dict["subscribe_user_name"]
                global users
                users[user_name_subs] = self
                print("Username " + user_name_subs + "is subscribed")
            elif "unsubscribe_user_name" in message_recv_dict:
                # remove username from users
                user_name_subs = message_recv_dict["unsubscribe_user_name"]
                global users
                del users[user_name_subs]
                print("Username " + user_name_subs + "is subscribed")
            elif "user_name_my" in message_recv_dict and "user_name_target" in message_recv_dict \
                    and "message" in message_recv_dict:
                user_name_source = message_recv_dict["user_name_my"]
                user_name_destination = message_recv_dict["user_name_target"]
                message = message_recv_dict["message"]

                if user_name_destination in users.keys():
                    delivery_dict = {"user_name_sender": user_name_source, "message": message}
                    global users
                    users[user_name_destination].sendMessage(json.dumps(delivery_dict))
                else:
                    print("Username: " + user_name_destination + " is not connected")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        # TODO check the client and  remove from dict


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

log.startLogging(sys.stdout)

# create a Twisted Web resource for our WebSocket server
wsFactory = WebSocketServerFactory(u"ws://127.0.0.1:8080")
wsFactory.protocol = MyServerProtocol
wsResource = WebSocketResource(wsFactory)

# create a Twisted Web WSGI resource for our Flask server
wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

# create a root resource serving everything via WSGI/Flask, but
# the path "/ws" served by our WebSocket stuff
rootResource = WSGIRootResource(wsgiResource, {b'ws': wsResource})

# create a Twisted Web Site and run everything
site = Site(rootResource)

reactor.listenTCP(8080, site)
reactor.run()


@app.route('/')
def page_home():
    return render_template('index.html')

#if __name__ == '__main__':


