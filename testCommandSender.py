import communicationUtilities
import commands
import logging

class TestCommandSender(object):
    def __init__(self):
        self.cs = communicationUtilities.CommandSender(self)
        logging.basicConfig(level = logging.DEBUG)
        self.allowedToSend = True

    def onResponse(self, response):
        logging.info(response)

    def start(self):
        while True:
            command = raw_input("Command: ")
            if self.allowedToSend or command == commands.INTERRUPT :
                self.cs.sendRequest(command)
            else:
                logging.info("Not allowed to send data!")

t = TestCommandSender()
t.start()
