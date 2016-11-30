import time
import communicationUtilities
import os
import logging

class TestCommandReceiver(object):
    def __init__(self):
        logging.basicConfig(level = logging.DEBUG)
        self.isInterrupted = False
        self.cr = communicationUtilities.CommandReceiver(self)
        self.cr.start()

    def handleInterrupt(self):
        logging.info("Interrupt handled")
        self.isInterrupted = False

    def start(self):
        while True:
            try:
                time.sleep(3)
                commandRequest, index = self.cr.commandRequests.popleft()
                self.cr.commandResponses.append((commandRequest, index))
            except IndexError:
                pass
            except KeyboardInterrupt:
                os.kill(os.getpid(), 9)
            if self.isInterrupted:
                self.handleInterrupt()

t = TestCommandReceiver()
t.start()
