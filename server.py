import socket
import os
from _thread import *
import threading
import psycopg2

# pip install psycopg2

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


# Connect to database
def connect_database():
    con = psycopg2.connect(host='127.0.0.1', database='publisher_subscriber', user='postgres', password='suasenhapostgres')
    return con


def disconnect_database(con):
    con.close()

def insert_node(cur, id, ip, gate):
    sql = "insert into ps.nodes values(" +str(id)+ ", '" +ip+ "', '" +gate+ "')"
    cur.execute(sql)
    con.commit()

def insert_message():
    #todo
    return

def insert_topic():
    #todo
    return

ServerSocket = socket.socket()
host = 'localhost'
port = 1233
ThreadCount = 0
clients = {} 

con = connect_database()
cur = con.cursor()
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
    insert_node(cur, 10, address[0], str(address[1]))

ServerSocket.close()