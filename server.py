import socket
import os
from _thread import *
import threading
import psycopg2

# pip install psycopg2

def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server\n'))
    id_node = get_node_id(cur, str(connection.getpeername()[0]))
    send_message_after_connect(cur, connection.getpeername()[0], connection)
    while True:
        try:
            data = connection.recv(2048)
            if data.decode('utf-8')[0] == 'M':
                reply = 'Server Says: mensagem enviada'
                store_message(cur, data.decode('utf-8'), data.decode('utf-8')[1:5], id_node, connection)
            else :
                reply = 'Server Says: mensagem enviada'
            if not data:
                break
            connection.sendall(str.encode(reply))
        except:
            break
    connection.close()


def connect_database():
    con = psycopg2.connect(host='127.0.0.1', database='publisher_subscriber', user='postgres', password='19972015')
    return con

def disconnect_database(con):
    con.close()

# def insert_node(cur, id, ip, gate):
    # sql = "insert into ps.nodes values(" +str(id)+ ", '" +ip+ "', '" +gate+ "')"
    # cur.execute(sql)
    # con.commit()

def insert_message(cur, id, corpo, id_pub, id_sub, id_topic):
    sql = "insert into ps.messages values(" + str(id) + ", '" + corpo + "', " + str(id_pub) + ", "+ str(id_sub) +", "+ str(id_topic)+")"
    cur.execute(sql)
    con.commit()


def get_last_message(cur):
    sql = "select id from ps.messages order by id desc limit 1"
    cur.execute(sql)
    id = cur.fetchall()
    if not id:
        return 0
    else:
        return id[0][0]

def get_last_topic(cur):
    sql = "select id from ps.topics order by id desc limit 1"
    cur.execute(sql)
    id = cur.fetchall()
    if not id:
        return 0
    else:
        return id[0][0]

def get_subscribers(cur, id_topic):
    sql = "select tn.id_sub, n.ip, n.porta from ps.topics_nodes tn join ps.nodes n on tn.id_sub = n.id where tn.id_topic = " + str(id_topic)
    cur.execute(sql)
    ids = cur.fetchall()
    if not ids:
        return None
    else:
        return ids

def get_node_id(cur, ip):
    sql = "select id from ps.nodes where ip = '" + ip+ "'"
    cur.execute(sql)
    id = cur.fetchone()
    if not id:
        return 0
    else:
        return id

def store_message(cur, corpo, topic_name, id_pub, connection):
    sql = "select id from ps.topics where name = '" + topic_name + "'"
    cur.execute(sql)
    id_topic = cur.fetchone()
    if not id_topic:
        id_topic = get_last_topic(cur) + 1
        sql = "insert into ps.topics values(" + str(id_topic) + ", '" + topic_name + "')"
        cur.execute(sql)
        con.commit()
    else:
        id_topic = id_topic[0]
    id = get_last_message(cur)
    id = id + 1
    subs = get_subscribers(cur, id_topic)
    id_pub = id_pub[0]
    for sub in subs:
        try:
            connection.sendto(str.encode(corpo), (sub[1], int(sub[2])))
        except:
            insert_message(cur, id, corpo, id_pub, sub[0], id_topic)

def send_message_after_connect(cur, ip_sub, connection):
    sql = "select m.id, m.corpo from ps.messages m join ps.nodes n on m.id_sub = n.id where n.ip = '" + ip_sub + "'"
    cur.execute(sql)
    messages = cur.fetchall()
    if not messages:
        connection.sendall(str.encode("Voce está atualizado"))
    for message in messages:
        print(message)
        try:
            connection.sendall(str.encode(message[1]))
            sql = "delete from ps.messages where id = "+ str(message[0])
            cur.execute(sql)
            con.commit()
        except:
            print("Cliente desconectado")

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
    start_new_thread(threaded_client, (Client,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()