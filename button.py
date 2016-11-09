import RPi.GPIO as GPIO
import time
import sys
import commands
import communicationUtilities
import logging

class Button(object):
    """Button which is attached to rasperry pi.

    Attributes:
        * buttonPin: GPIO pin where the button is connected to
        * allowedToSend: indicates if button is allowed to send a command or not;
        Button is not allowed to change this value by itself
        * cs: An instance of CommandSender, which sends starting commands to the driller
    """
    def __init__(self, buttonPin = 18):
        """Constructor; sets attributes.

        Args:
            see attributes

        Returns:
            None

        Raises:
            None
        """
        self.buttonPin = buttonPin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.cs = communicationUtilities.CommandSender(self)
        self.allowedToSend = True
        logging.basicConfig(level = logging.DEBUG)

    def onResponse(self, response):
        """Printing the command response."""
        logging.debug(response)

    def start(self):
        """Listens if the button is pressed and sends a starting command to the driller,
        if we allowed to."""
        while True:
            if GPIO.input(self.buttonPin) == False and self.allowedToSend:
                self.cs.sendRequest(commands.REQUEST_STARTDRILLING)
            time.sleep(0.1)

if __name__ == "__main__":
    button = Button()
    button.start()
