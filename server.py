import socket
import os
from _thread import *
import threading
import psycopg2

# pip install psycopg2

def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server\n'))
    id_pub = get_node_id(cur, str(connection.getpeername()[0]))
    while True:
        try:
            data = connection.recv(2048)
            if data.decode('utf-8')[0] == 'M':
                reply = 'Server Says: mensagem enviada'
                store_message(cur, data.decode('utf-8'), data.decode('utf-8')[1:5], id_pub)
            else :
                reply = 'Server Says: mensagem enviada'
            if not data:
                break
            connection.sendall(str.encode(reply))
        except:
            break
    connection.close()


def connect_database():
    con = psycopg2.connect(host='127.0.0.1', database='publisher_subscriber', user='postgres', password='suasenha')
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
    sql = "select id_sub from ps.topics_nodes where id_topic = " + str(id_topic)
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
    for id_sub in subs:
        insert_message(cur, id, corpo, id_pub, id_sub[0], id_topic)

def send_message(cur):
    sql = "select id, corpo, ip from ps.messages m join ps.nodes n on m.id_sub = n.id"
    cur.execute(sql)
    messages = cur.fetchall()
    for message in messages:
        # enviar mensagem para message.ip
        #se der certo
        sql = "delete from ps.messages where id = "+ message.id
        cur.execute(sql)
        con.commit()

def subscribe_on_topic(cur, id_topic, id_node):
	sql = "select * from ps.topics_nodes where id_topic = '" + str(id_topic) + "' and id_sub = '" + str(id_node) + "'"
	cur.execute(sql)
	is_subscribed = cur.fetchall()
	if not is_subscribed:
		sql = "insert into ps.topics_nodes values(" + str(id_topic) + "," + str(id_node) + ")"
		cur.execute(sql)
		con.commit()
		return 'Successfully subscribed!'
	else:
		return 'Already subscribed'

def unsubscribe_on_topic(cur, id_topic, id_node):
	sql = "select * from ps.topics_nodes where id_topic = '" + str(id_topic) + "' and id_sub = '" + str(id_node) + "'"
	cur.execute(sql)
	is_subscribed = cur.fetchall()
	if is_subscribed:
		sql = "delete from ps.topics_nodes id_topic = '" + str(id_topic) + "' and id_sub = '" + str(id_node) + "'"
		cur.execute(sql)
		con.commit()
		return 'You are not subscribed to this topic anymore.'
	else:
		return 'Subscription not found'
        
def get_subscribed_topics(cur, id_node):
	sql = "select t.name from ps.topics t join ps.topics_nodes n on (t.id_topic = n.id_topic) where n.id_sub = '" + str(id_node) + "'"
	cur.execute(sql)
	topic_names = cur.fetchall()
	if not topic_list:
		return None
	else:
		return topic_names

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
