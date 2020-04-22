import socket
import os
from _thread import *
import threading


ServerSocket = socket.socket()
host = '192.168.0.110'
port = 1233
ThreadCount = 0
clients = {} 
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)

def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server\n'))
    while True:
        try:
            data = connection.recv(2048)
            reply = 'Server Says: ' + data.decode('utf-8')
            if not data:
                break
            connection.sendall(str.encode(reply))
        except:
            break
    connection.close()

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()