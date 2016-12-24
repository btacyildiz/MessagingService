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

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
import json


message_to_send = ""


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        def hello():

            self.sendMessage(json.dumps({"heart_beat": "1"}).encode('utf8'), isBinary=False)
            self.factory.reactor.callLater(1, hello)
            if message_to_send:
                print "MessageToSend: " + message_to_send
                self.sendMessage(message_to_send, isBinary=False)
                global message_to_send
                message_to_send = ""

        hello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Message: {0}".format(payload.decode('utf8')))
        else:
            print("Binary message is received")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys
    import thread

    from twisted.python import log
    from twisted.internet import reactor

    import thread


    def someFunc():
        user_name_my = raw_input("Enter username:")
        user_name_target = raw_input("Enter target username:")

        #print("Setup UserName: " + user_name_my + " UseNameTarget: " + user_name_target)
        #send username to server
        #self.sendMessage(json.dumps({"subscribe_user_name": user_name_my}).encode('utf8'), isBinary=False)
        global  message_to_send
        message_to_send = json.dumps({"subscribe_user_name": user_name_my}).encode('utf8')
        user_quit = False
        while user_quit is False:
            print("Enter Message To Send: ")
            message_send = raw_input("Enter Message To Send: ")
            if message_send == "q":
                user_quit = True
            else:
                message_send_dict = {"user_name_my": user_name_my, "user_name_target": user_name_target,
                                     "message": message_send}
                message_to_send = json.dumps(message_send_dict).encode('utf8')
                print "Entered: " + message_to_send
                #self.sendMessage(json.dumps(message_send_dict).encode('utf8'), isBinary=False)


    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyClientProtocol

    thread.start_new_thread(someFunc, ())

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()





