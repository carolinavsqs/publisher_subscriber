import pickle
import socket
import os
from _thread import *
import threading
import psycopg2

from message import Message

# pip install psycopg2


HOST = 'localhost'
PORT = 1233


def authenticate_node(connection):
    """
    Handles connections from new nodes and nodes already registered
    :param connection:
    :return:
    """
    msg = connection.recv(2048)
    msg = pickle.loads(msg)
    if msg.message_type == 'connect':
        ip = connection.getpeername()[0]
        gate = connection.getpeername()[1]
        node_id = msg.node_id

        # Node already has a system ID
        if node_id:
            # Updates the user's address
            if ip != get_node_ip(cur, node_id) or gate != get_node_gate(cur, node_id):
                update_node(cur, node_id, ip, gate)

            msg = pickle.dumps(Message(node_id, 'accept', "Welcome to the Server\n"))
            connection.send(msg)

            print("Client " + str(node_id) + ", logged with address " + str(ip) + ":" + str(gate))

        #  New node on system
        else:
            new_id = insert_node(cur, ip, gate)
            msg = pickle.dumps(Message(new_id, 'connect', "Welcome to the Server\n"))
            connection.send(msg)
            print("New client " + str(new_id) + ", logged with address " + str(ip) + ":" + str(gate))


def connect_node():
    # TODO
    pass


def publish_message():
    # TODO
    pass


def list_topics(connection):
    """
    Returns a list of topics available to subscribe
    :param connection:
    :return:
    """
    topics_list = get_topics(cur)

    msg_string = 'List of available topics: \n'
    for topic in topics_list:
        msg_string += topic[0] + '\n'

    msg = pickle.dumps(Message('Broker', 'response', msg_string))
    connection.send(msg)


def subscribe_topic():
    # TODO
    pass


def unsubscribe_topic():
    # TODO
    pass


FUNCTIONS = {
    'connect': connect_node,
    'publish': publish_message,
    'list': list_topics,
    'subscribe': subscribe_topic,
    'unsubscribe': unsubscribe_topic,
}


def threaded_client(connection):
    authenticate_node(connection)
  
    id_node = get_node_id(cur, str(connection.getpeername()[0]))
    send_message_after_connect(cur, connection.getpeername()[0], connection)

    while True:
        msg = connection.recv(2048)
        msg = pickle.loads(msg)
        operation = FUNCTIONS.get(msg.message_type, False)

        if operation:
            operation(connection)
        else:
            connection.send(str.encode("Invalid operation"))

        try:
            id_pub = get_node_id(cur, str(connection.getpeername()[0]))
            data = connection.recv(2048)
            if data.decode('utf-8')[0] == 'M':
                reply = 'Server Says: mensagem enviada'
                store_message(cur, data.decode('utf-8'), data.decode('utf-8')[1:5], id_node, connection)
            else :
                reply = 'Server Says: mensagem enviada'
            if not data:
                break
            connection.sendall(str.encode(reply))
        except error:
            break
    connection.close()


def connect_database():
    con = psycopg2.connect(host='127.0.0.1', database='publisher_subscriber', user='postgres', password='senha')
    return con


def disconnect_database(con):
    con.close()

def insert_node(cur, ip, gate):
    sql = 'SELECT id FROM ps.nodes ORDER BY id DESC LIMIT 1'
    cur.execute(sql)
    node_id = cur.fetchone()[0]

    node_id = int(node_id) + 1
    sql = "insert into ps.nodes values(" +str(node_id)+ ", '" +str(ip)+ "', '" + str(gate) + "')"
    cur.execute(sql)
    con.commit()
    return node_id


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


def get_node_ip(cur, id):
    sql = "select ip from ps.nodes where id =  " + str(id)
    cur.execute(sql)
    ip = cur.fetchone()
    if not ip:
        return False
    else:
        return ip

def get_node_gate(cur, id):
    sql = "select porta from ps.nodes where id =  " + str(id)
    cur.execute(sql)
    gate = cur.fetchone()
    if not gate:
        return False
    else:
        return gate

def get_topics(cur):
    sql = "select name from ps.topics"
    cur.execute(sql)
    topics = cur.fetchall()
    if not topics:
        return False
    else:
        return topics

def update_node(cur, id, ip, gate):
    sql = "update ps.nodes set ip = '" + str(ip) + "',porta = '" + str(gate) + "' where id = " + str(id)
    cur.execute(sql)
    con.commit()


def store_message(cur, corpo, topic_name, id_pub):
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

ThreadCount = 0
clients = {} 

con = connect_database()
cur = con.cursor()
try:
    ServerSocket.bind((HOST, PORT))
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
