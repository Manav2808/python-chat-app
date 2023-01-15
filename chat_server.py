import pickle
import socket
import threading

class Server:
    def __init__(self):
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.PORT = 5050
        self.ADDR = (self.SERVER, self.PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

        self.totalConnections = 0
        self.clientNames = []
        self.connList = []
        self.chatMsgsList = []

    def startServer(self):
        self.server.listen()
        print(f"Server started at {self.SERVER}")

        while True:
            if self.totalConnections < 20:
                conn, addr = self.server.accept()
                clientThread = threading.Thread(target = self.handleClient, args = (conn, addr))
                clientThread.start()
                self.totalConnections += 1

    def handleClient(self, conn, addr):
        connected = True

        clientName = pickle.loads(conn.recv(64))
        self.clientNames.append(clientName)
        self.connList.append(conn)

        print(f"{clientName} ({addr[0]}) joined the server")

        for connections in self.connList:
            connections.send(pickle.dumps((self.clientNames, self.chatMsgsList)))

        while connected:
            msg = pickle.loads(conn.recv(64))

            if msg == "Disconnect":
                connected = False

                conn.send(pickle.dumps("Close Connection"))

                print(f"{clientName} left the server")

                self.clientNames.remove(clientName)
                self.connList.remove(conn)
                self.totalConnections -= 1
            else:
                if len(self.chatMsgsList) == 10:
                    self.chatMsgsList.pop(0)
                    self.chatMsgsList.append([clientName, msg])
                else:
                    self.chatMsgsList.append([clientName, msg])

                print(f"{clientName}: {msg}")

            for connections in self.connList:
                connections.send(pickle.dumps((self.clientNames, self.chatMsgsList)))

        conn.close()

server = Server()
server.startServer()
