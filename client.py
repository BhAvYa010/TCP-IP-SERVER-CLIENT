import socket
import threading

def enter_server():    
    # Store the ip and port number for connection
    ip = "localhost "
    port = 5555
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to a host
    client.connect((ip, port))
    while True:
        # TODO: add loading ...s
        message = client.recv(1024).decode('ascii')
        if message == 'NICK':
            global nickname
            nickname = input("Enter your name:")
            client.send(nickname.encode('ascii'))
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii'))

enter_server()
# TODO: maybe add receive_thread as github
write_thread = threading.Thread(target=write)
write_thread.start()