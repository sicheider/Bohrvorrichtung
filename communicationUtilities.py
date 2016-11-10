import socket
import threading
import select
import collections
import os
import sys
import logging
import commands

class ConnectionAcceptor(threading.Thread):
    """Class for accepting new socet connections in a thread.

    Attributes:
        * master: Class which handles the connections; must have a list as attribute named "connections"
        * host: host ipadress
        * port: port to listen
    """
    def __init__(self, master, host, port):
        """Constructor; sets the attributes.
        Args:
           see Attributes

        Returns:
            None

        Raises:
            None
        """
        threading.Thread.__init__(self)
        self.deamon = True
        self.host = host
        self.port = port
        self.master = master 
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(10)
        except socket.error as e:
            logging.warning(str(e))

    def run(self):
        """Start main listeningloop and writes new connections to connectionWorker.connections.
        
        Args:
            None
            
        Returns:
            None
        
        Raises:
            None
        """
        while True:
            conn, addr = self.s.accept()
            logging.info("Connection accepted: " + str(addr[0]) + " " + str(addr[1]))
            conn.setblocking(0)
            self.master.connections.append(conn)

class CommandReceiver(threading.Thread):
    """Receives command requests and sends command responses.

    Attributes:
        * master: A class that handles the commands; must have a boolean attribute named "isInterrupted"
        * connections: A list where all connections are stored
        * commandRequests: A queue where all received (commandRequests, con) are stored
        * commandResponses: A queue where all (commandResponses, con) are stored, which have to be send
        * timeout: Blocking time for reading sockets
        * ca: An instance of ConnectionAcceptor which accepts new connections and writes them to connections
    """
    def __init__(self, master, host = "", port = 54321, timeout = 0.2):
        """Constructor; sets attributes and starts ConnectionAcceptor

        Args:
            see Attributes
        
        Returns:
            None

        Raises:
            None
        """
        threading.Thread.__init__(self)
        self.master = master
        self.deamon = True
        self.connections = []
        self.commandRequests = collections.deque()
        self.commandResponses = collections.deque()
        self.timeout = timeout
        self.ca = ConnectionAcceptor(self, host, port)
        self.ca.start()

    def receiveCommandRequests(self):
        """Reads all incoming command requests and writes them to commandRequests.
        Interrupts the master, if necessary.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        try:
            reading, writing, error = select.select(self.connections, [], [], self.timeout)
        except KeyboardInterrupt:
            os.kill(os.getpid(), 9)
        for con in reading:
            try:
                commandRequest = con.recv(256)
                if commandRequest == "":
                    logging.info("Connection closed: " + str(con))
                    self.connections.remove(con)
                elif commandRequest == commands.INTERRUPT:
                    logging.info("Master interrupted from: " + str(con))
                    self.master.isInterrupted = True
                    con.sendall(commands.INTERRUPT)
                else:
                    logging.debug("Command received: " + commandRequest)
                    self.commandRequests.append((commandRequest, con))
            except socket.error as e:
                logging.warning(str(e))

    def sendCommandResponses(self):
        """Sends all command responses stored in commandResponses.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        while self.commandResponses:
            commandResponse, con = self.commandResponses.popleft()
            try:
                logging.debug("Sending response: " + commandResponse)
                con.sendall(commandResponse)
            except socket.error as e:
                logging.warning(str(e))

    def run(self):
        """Starts main receiving and sending loop in a thread."""
        while True:
            self.receiveCommandRequests()
            self.sendCommandResponses()

class CommandSender(object):
    """Class to send command requests and wait for command responses.

    Attributes:
        * master: A class which wants to send command requests; must have a boolean attributes named "allowedToSend"
        and and implement a method onResponse(response)
        * sendInterrupt: If true CommandSender sends an interrupt command to CommandReceiver
        * timeout: Blocking time for reading socket
        * s: socket, which is connected to a commandReceiver
    """
    def __init__(self, master, host = "localhost", port = 54321, timeout = 0.2):
        """Constructor; sets attributes and connects the socket to a CommandReceiver.

        Args:
            * host: host to connect to
            * port: port to connect to
            * rest: see attributes

        Returns:
            None

        Raises:
            None
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master = master
        self.timeout = timeout
        self.sendInterrupt = False
        try:
            self.s.connect((host, port))
            self.s.setblocking(0)
        except socket.error as e:
            logging.error("Can not connect!")
            logging.error(str(e))
            sys.exit(1)

    def receiveResponse(self):
        """Waits until a command response has arrived. Sends an interrupt command if necessary.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        run = True
        while run:
            reading, writing, error = select.select([self.s], [], [], self.timeout)
            if reading:
                try:
                    response = reading[0].recv(256)
                    run = False
                    self.master.onResponse(response)
                    self.master.allowedToSend = True
                except socket.error as e:
                    logging.warning(str(e))
            if self.sendInterrupt:
                self.s.sendall(commands.INTERRUPT)

    def sendRequest(self, commandRequest):
        """Sends a command request to a CommandReceiver. Waits for the response in a thread.

        Args:
            * commandRequest: the command to be send

        Returns:
            None

        Raises:
            None
        """
        try:
            self.s.sendall(commandRequest)
            self.master.allowedToSend = False
            thread = threading.Thread(target = self.receiveResponse)
            thread.start()
        except socket.error as e:
            logging.warning(str(e))

    def close(self):
        """Closes the connection to the CommandReceiver."""
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
