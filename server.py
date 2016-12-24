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

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import json

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
            print("Debug message received: {0}".format(payload.decode('utf8')))
            # check if it is for subscription

            message_recv_dict = json.loads(payload.decode('utf8'))
            if "subscribe_user_name" in message_recv_dict:

                user_name_subs = message_recv_dict["subscribe_user_name"]
                global users
                users[user_name_subs] = self
                print("Username " + user_name_subs + "is subscribed")
            elif "user_name_my" in message_recv_dict and "user_name_target" in message_recv_dict \
                    and "message" in message_recv_dict:
                user_name_source = message_recv_dict["user_name_my"]
                user_name_destination = message_recv_dict["user_name_target"]
                message = message_recv_dict["message"]

                if user_name_destination in users.keys():
                    delivery_dict = {"user_name_sender": user_name_source, "message": message}
                    users[user_name_destination].sendMessage(json.dumps(delivery_dict))
                else:
                    print("Username: " + user_name_destination + " is not connected")


        """if "berkay" in users.keys() and "ayse" in users.keys():
            users["berkay"].sendMessage("berkay says hello", isBinary)
            users["ayse"].sendMessage("ayse says hello", isBinary)
        """

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()