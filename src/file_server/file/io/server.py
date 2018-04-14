import socket
from collections import deque
from threading import Thread

from file_server.file.io import ByteBuffer

from .easy_socket import EasySocket 
from file_server.web.account import Account

from time import time

from .hub import Hub

class FileServer(Hub):
    def __init__(self, directory, port=EasySocket.PORT):

        super(self.__class__, self).__init__(directory, port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.shutdown = False
        self.webserver = None

    def kill(self):
        super(self.__class__, self).kill()

        # Shut down webserver
        if self.webserver is not None:
            self.webserver.force_stop()

        # Stop file server listening
        self.shutdown = True
        self.sock.close()

        # Shut down file server connections
        for conn in self.connections:
            conn.shutdown = True

    def start(self, serve=True):
        self.sock.bind((socket.gethostname(), self.port))
        self.sock.listen(5)

        if serve:
            self.serve()

    def serve(self):
        print("Waiting for connections on " + str(socket.gethostname()))
        while not self.shutdown:
            try:
                clientsocket, address = self.sock.accept()
            except OSError:
                continue
            print("Connection recieved: " + clientsocket.getpeername()[0])

            session_length = ByteBuffer(clientsocket.recv(4)).read_int()
            session = ByteBuffer(clientsocket.recv(session_length)).read_string()

            try:
                account = Account.sessions[session]
            except KeyError:
                print("Count not load account")
                clientsocket.send(ByteBuffer(b"0")).bytes()

            clientsocket.send(ByteBuffer(b"1").bytes())

            connection = ServerConnection(
                account,
                clientsocket.getpeername()[0],
                clientsocket,
                self
            )
            self.connections.append(connection)
            connection.start()

    def send_packet(self, packet):
        for conn in self.connections:
            conn.queue_packet(packet)

class ServerConnection(Thread):
    def __init__(self, account, name, socket, server):
        super().__init__()
        self.account = account
        self.client_host = name
        self.sock = EasySocket(self, socket)
        self.server = server
        self.packet_queue = deque()
        self.shutdown = False
        self.connect_time = time()
        self.data_recieved = 0
        self.files_recieved = 0
        self.data_sent = 0
        self.files_sent = 0
        self.transferring = None
        self.transfer_progress = 0

    @property
    def directory(self):
        return self.server.directory

    @property
    def file_event_handler(self):
        return self.server.file_event_handler

    def run(self):
        while (not self.shutdown):
            try: 
                # Wait for a packet
                with self.sock.read_packet():
                    self.server.prepare_packets(self)
                
                while self.sock.read().read_bool(): # Handle the rest of the packets
                    with self.sock.read_packet():
                        pass

                self.sock.send(ByteBuffer.from_bool(not len(self.packet_queue) == 0))
                while not len(self.packet_queue) == 0:
                    self.sock.send_packet(self.packet_queue.pop())
                    self.sock.send(ByteBuffer.from_bool(not len(self.packet_queue) == 0))

            except ConnectionResetError as e:
                print(e)
                break

        print("Connection to client \"{}\" has been lost".format(self.client_host))

        connections = self.server.connections
        for i in range(len(connections)):
            if connections[i] is self:
                del connections[i]

    def queue_packet(self, packet):
        self.packet_queue.append(packet)