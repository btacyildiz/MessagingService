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


#message_to_send = ""
client_conn = None


def submission_loop():
    print "Info: enter 'q' to quit"
    print "Enter username: "
    user_name_my = raw_input()
    print "Enter target username: "
    user_name_target = raw_input()

    # print("Setup UserName: " + user_name_my + " UseNameTarget: " + user_name_target)
    # send username to server
    # self.sendMessage(json.dumps({"subscribe_user_name": user_name_my}).encode('utf8'), isBinary=False)
    message_to_send = json.dumps({"subscribe_user_name": user_name_my}).encode('utf8')
    if client_conn is not None:
        client_conn.sendMessage(message_to_send)
    else:
        print "Unable to subscribe, client is not connected"

    user_quit = False
    while user_quit is False:
        print("Enter Message To Send: ")
        message_send = raw_input()
        if message_send == "q":
            user_quit = True
        else:
            message_send_dict = {"user_name_my": user_name_my, "user_name_target": user_name_target,
                                 "message": message_send}
            message_to_send = json.dumps(message_send_dict).encode('utf8')
            # print "Entered: " + message_to_send
            if client_conn is not None:
                client_conn.sendMessage(message_to_send)
            else:
                print "Unable to send message, client is not connected"
    # user decided to quit
    message_to_send = json.dumps({"unsubscribe_user_name": user_name_my}).encode('utf8')
    if client_conn is not None:
        client_conn.sendMessage(message_to_send)
    else:
        print "Unable to unsubscribe, client is not connected"
    client_conn.disconnect()


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        # start input thread
        thread.start_new_thread(submission_loop, ())
        # set client connection as global
        global client_conn
        client_conn = self

        def heart_beat():
            self.sendMessage(json.dumps({"heart_beat": "1"}).encode('utf8'), isBinary=False)
            # call heart_beat function every 3 seconds to keep connection alive
            # TODO is this necessary?
            self.factory.reactor.callLater(3, heart_beat)
        heart_beat()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                payload_utf8_decoded = payload.decode('utf8')
                payload_parsed = json.loads(payload_utf8_decoded)
                if "heart_beat" in payload_parsed:
                    print "Heart beat"
                elif "user_name_sender" in payload_parsed and "message" in payload_parsed:
                    print payload_parsed["user_name_sender"] + ": " + payload_parsed["message"]
                else:
                    print "Payload does not contain necessary info"
            except Exception, e:
                print "Exception parsing incoming message", str(e)
        else:
            print("Binary message is received")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        global client_conn
        client_conn = None


if __name__ == '__main__':

    import sys
    import thread

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory(u"ws://ec2-35-162-164-18.us-west-2.compute.amazonaws.com/ws")
    factory.protocol = MyClientProtocol

    reactor.connectTCP("ec2-35-162-164-18.us-west-2.compute.amazonaws.com", 8080, factory)
    reactor.run()





