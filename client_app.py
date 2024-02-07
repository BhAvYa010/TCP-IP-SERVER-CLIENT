import sys
import socket
import threading

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

from client_gui import Ui_ClientWindow

# profileImageLocation = "ui/resources/generic-profile-pic.png"
profileName = "user"
serverIP = "localhost"
localIP = socket.gethostbyname(socket.gethostname())
serverPort = 8888
isConnected = False

class Window(QMainWindow, Ui_ClientWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        global serverIP
        serverIP = localIP
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.actionChange_Profile.triggered.connect(self.changeProfile)
        self.actionQuit.triggered.connect(self.closeEvent)

        self.actionChange_Server_Address.triggered.connect(self.changeServerAddress)
        self.actionConnect.triggered.connect(self.connectServer)
        self.actionDisconnect.triggered.connect(self.disconnectServer)

        self.tboxMessage.returnPressed.connect(self.sendMessage)
        self.btnSend.clicked.connect(self.sendMessage)

    def closeEvent(self, event):
        self.disconnectServer()
        self.close()

    def changeProfile(self):
        dialog = ChangeProfileDialog(self)
        dialog.exec()
        if dialog.Accepted:
            if isConnected:
                client.send(f"NAM:{profileName}".encode('ascii'))
                
            self.labelProfileName.setText(profileName)
            self.statusbar.showMessage(f"Profile changed", 3000)

    def changeServerAddress(self):
        dialog = ChangeServerAddressDialog(self)
        dialog.exec()
        if dialog.Accepted and isConnected:
            self.connectServer()

    def connectServer(self):
        global client, isConnected
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((serverIP, serverPort))
        except:
            QMessageBox.warning(self, "Connection failed", f"Error connecting to server {serverIP}:{serverPort}")
            self.statusbar.showMessage(f"Connection failed", 3000)
            return
        
        while True:
            message = client.recv(1024).decode('ascii')
            if message == 'NAM':
                client.send(f"NAM:{profileName}".encode('ascii'))
            elif message == 'CON':
                self.statusbar.showMessage(f"Connected to server {serverIP}:{serverPort}", 3000)
                isConnected = True
                self.labelIsConnected.setText("Online")
                break

    def disconnectServer(self):
        global isConnected
        if isConnected:
            client.send("DIS".encode('ascii'))

        isConnected = False
        self.labelIsConnected.setText("Offline")

        try:
            client.close()
            self.statusbar.showMessage(f"Disconnected from server {serverIP}:{serverPort}", 3000)
        except:
            return

    def sendMessage(self):
        if not isConnected:
            QMessageBox.warning(self, "Not connected to server", "Please connect to a server")
            return
        
        if not self.tboxMessage.text():
            self.statusbar.showMessage("Please enter a message to send", 3000)
            self.tboxMessage.setFocus()
            return
        
        client.send(self.tboxMessage.text().encode('ascii'))
        self.tboxMessage.setText("")
        self.tboxMessage.setFocus()

class ChangeProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/client_changeProfile.ui", self)
        self.tboxName.setText("" if profileName == "user" else profileName)

    def accept(self):
        global profileName
        profileName = self.tboxName.text()
        self.close()

class ChangeServerAddressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/client_changeServerAddress.ui", self)
        self.tboxIP.setText("" if serverIP == localIP else serverIP)
        self.tboxIP.setPlaceholderText(f"Default: {localIP}")
        self.tboxPort.setValue(serverPort)

    def accept(self):
        global serverIP, serverPort
        serverIP = localIP if self.tboxIP.text() == "" else self.tboxIP.text()
        serverPort = self.tboxPort.value()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())