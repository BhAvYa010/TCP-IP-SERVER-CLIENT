import sys
import threading
import socket

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QRegion

from server_gui import Ui_ServerWindow

chatCount = 0
serverIP = "localhost"
serverPort = 8888

def addChat(sender,msg):
    labelMessages.setText(labelMessages.text() + f"<p><span style=\" font-weight:600;\">{sender}: </span>{msg}</p>")
    scrollArea.verticalScrollBar().setValue(scrollArea.verticalScrollBar().maximum())
    
class Window(QMainWindow, Ui_ServerWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        global labelMessages, scrollArea, serverIP
        labelMessages, scrollArea = self.setupUi(self)
        serverIP = socket.gethostbyname(socket.gethostname())
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.actionChange_Port.triggered.connect(self.changePort)
        self.actionStart_Server.triggered.connect(self.startServer)

        self.actionQuit.triggered.connect(self.close)

    def changePort(self):
        dialog = SetPortDialog(self)
        dialog.exec()

    def startServer(self):
        global server, clients, clientnames
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the server to IP Address
        server.bind((serverIP, serverPort))
        # Start Listening Mode
        server.listen()

        # List to contain the Clients getting connected and nicknames
        clients = []
        clientnames = []

        thread = threading.Thread(target=self.handleServer, args=())
        thread.start()
        self.statusbar.showMessage(f"Server started on {serverIP}:{serverPort}", 3000)

    def handleServer(self):
        while True:
            client, address = server.accept()
            self.statusbar.showMessage(f"Connected with {str(address)}", 3000)
            
            client.send('NAM'.encode('ascii'))
            name = client.recv(1024).decode('ascii').split(':')[1]
            clientnames.append(name)

            clients.append(client)
            print(f' joined the Chat')
            self.statusbar.showMessage(f"{str(name)} joined the chat", 3000)
            client.send('CON'.encode('ascii'))

            # Handling Multiple Clients Simultaneously
            thread = threading.Thread(target=self.handleClient, args=(client,))
            thread.start()

    def handleClient(self, client):
        index = clients.index(client)
        name = clientnames[index]
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    break
                message = message.decode('ascii')
                if message.split(':')[0] == 'NAM':
                    clientnames[index] = message.split(':')[1]
                    self.statusbar.showMessage(f"{name} renamed to {clientnames[index]}", 3000)
                    name = clientnames[index]
                    return
                elif message == 'DIS':
                    self.statusbar.showMessage(f"{name} left the chat", 3000)
                    client.close()
                    clients.remove(client)
                    clientnames.remove(name)
                    return
                addChat(name, message)


            except socket.error:
                if client in clients:
                    index = clients.index(client)
                    client.close()
                    clients.remove(client)
                    name = clientnames[index]
                    self.statusbar.showMessage(f'Connection lost with {name}', 3000)
                    clientnames.remove(name)
                    return
                break

class SetPortDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/server_setPort.ui", self)
        self.tboxPort.setValue(serverPort)

    def accept(self):
        global serverPort
        serverPort = self.tboxPort.value()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())