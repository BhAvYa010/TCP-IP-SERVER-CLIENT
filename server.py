import threading
import socket

# Now this Host is the IP address of the Server, over which it is running.
# I've user my localhost.
host = "localhost"
port = 5555  # Choose any random port which is not so common (like 80)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the server to IP Address
server.bind((host, port))
# Start Listening Mode
server.listen()
# List to contain the Clients getting connected and nicknames
clients = []
nicknames = []

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            print(message)  # As soon as message received, broadcast it.

        except socket.error:
            remove(client)
            break

def remove(client, reason=""):
    if client in clients:
        index = clients.index(client)
        client.close()
        clients.remove(client)
        nickname = nicknames[index]
        print(f'Connection lost with {nickname}!')
        nicknames.remove(nickname)
        return


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        # Ask the clients for Nicknames
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        nicknames.append(nickname)
        clients.append(client)

        print(f'{nickname} joined the Chat')
        # client.send('Welcome to the Server!'.encode('ascii')) # Will not work if client does not have receive thread

        # Handling Multiple Clients Simultaneously
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Calling the main method
print('Server is Listening ...')
receive()
