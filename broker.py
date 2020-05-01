import pickle
import socket
from _thread import *
import psycopg2

from message import Message

# pip install psycopg2


HOST = 'localhost'
PORT = 1232
CLIENTS = []


def authenticate_node(connection):
    """
    Lida com conexões novas e já existentes de nós
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

            msg = pickle.dumps(Message(node_id, 'accept', "Bem-vindo(a) ao servidor.\n", ''))
            connection.send(msg)

            print("Cliente " + str(node_id) + " fez login com o endereço " + str(ip) + ":" + str(gate))

        #  New node on system
        else:
            new_id = insert_node(cur, ip, gate)
            msg = pickle.dumps(Message(new_id, 'connect', "Bem-vindo(a) ao servidor.\n", ''))
            connection.send(msg)
            print("Novo cliente " + str(new_id) + " fez login com o endereço " + str(ip) + ":" + str(gate))


def publish_message(connection, msg):
    store_message(connection, msg)


def list_topics(connection, msg):
    """
    Devolve a lista de tópicos disponíveis
    :param connection:
    :return:
    """
    topics_list = get_topics(cur)

    msg_string = 'Lista de tópicos disponíveis: \n'
    for topic in topics_list:
        msg_string += str(topic[0]) + ' - ' + topic[1] + '\n'

    msg = pickle.dumps(Message('Broker', 'response', msg_string, ''))
    connection.send(msg)


def subscribe_topic(connection, msg):
    """
    Inscreve em um tópico se ele existir
    :param connection:
    :param msg:
    :return:
    """
    sql = "select * from ps.topics_nodes where id_topic = " + msg.topic + " and id_sub = " + msg.node_id
    cur.execute(sql)
    is_subscribed = cur.fetchall()
    if not is_subscribed:
        sql = "insert into ps.topics_nodes values(" + msg.topic + "," + msg.node_id + ")"
        cur.execute(sql)
        con.commit()
        string_msg = 'Inscrito(a) com sucesso no tópico ' + msg.topic + '.'

    else:
        string_msg = 'Você já está inscrito(a) no tópico ' + msg.topic + '!'

    msg = Message(msg.node_id, 'response', string_msg, msg.topic)
    msg = pickle.dumps(msg)
    connection.send(msg)


def get_subscribed_topics(connection, msg):
    """
    Devolve a lista de tópicos inscritos pelo nó
    :param connection:
    :param msg:
    :return:
    """
    sql = "select t.name, t.id from ps.topics t join ps.topics_nodes n on (t.id = n.id_topic) where n.id_sub = " + msg.node_id
    cur.execute(sql)
    subscribed_topics = cur.fetchall()

    if not subscribed_topics:
        string_msg = 'Você não está inscrito em nenhum tópico.'
        if_topics = False
    else:
        string_msg = 'Você está inscrito nos seguintes tópicos:\n'
        if_topics = True
        for topic in subscribed_topics:
            string_msg += str(topic[1]) + ' - ' + topic[0] + '\n'

    msg = pickle.dumps(Message(msg.node_id, 'list', string_msg, if_topics))
    connection.send(msg)


def unsubscribe_topic(connection, msg):
    """
    Remove a inscrição de um nó caso ele esteja inscrito no tópico
    :param connection:
    :param msg:
    :return:
    """
    sql = "select * from ps.topics_nodes where id_topic = '" + msg.topic + "' and id_sub = '" + msg.node_id + "'"
    cur.execute(sql)
    is_subscribed = cur.fetchall()
    if is_subscribed:
        sql = "delete from ps.topics_nodes where id_topic = '" + msg.topic + "' and id_sub = '" + msg.node_id + "'"
        cur.execute(sql)
        con.commit()
        string_msg = 'Você não está mais inscrito no tópico ' + msg.topic + '.'
    else:
        string_msg = 'Inscrição não encontrada'

    msg = Message(msg.node_id, 'response', string_msg, msg.topic)
    msg = pickle.dumps(msg)
    connection.send(msg)

# Dicionário de funções disponíveis ao nó
FUNCTIONS = {
    'publish': publish_message,
    'list_all': list_topics,
    'subscribe': subscribe_topic,
    'unsubscribe': unsubscribe_topic,
    'list_subscribed': get_subscribed_topics,
}


def threaded_client(connection):
    """
    Thread de cada nó com o loop principal aguardando as requisições
    :param connection:
    :return:
    """
    authenticate_node(connection)
  
    id_node = get_node_id(cur, str(connection.getpeername()[0]))
    send_message_after_connect(cur, connection.getpeername()[0], connection)

    while True:
        try:
            msg = connection.recv(2048)
            msg = pickle.loads(msg)
            operation = FUNCTIONS.get(msg.message_type, False)

            if operation:
                operation(connection, msg)
            else:
                connection.send(str.encode("Operação inválida"))
        except error:
            print(error)
            client = str(connection.getpeername()[0]) + ':' + str(connection.getpeername()[1])
            print("O cliente " + client + ' saiu do servidor')
            CLIENTS.remove(client)

    connection.close()


def connect_database():
    con = psycopg2.connect(host='127.0.0.1', database='publisher_subscriber', user='postgres', password='suasenha')
    return con


def disconnect_database(con):
    con.close()

def insert_node(cur, ip, gate):
    """
    Insere o registro de um novo nó com seu ID no banco de dados
    :param cur:
    :param ip:
    :param gate:
    :return:
    """
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
        return []
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
        return 0
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
    sql = "select id, name from ps.topics"
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


def store_message(connection, msg):
    """
    Envia as mensagens recém publicadas para os nós online e persiste as mensagens dos nós que estão offline
    :param connection:
    :param msg:
    :return:
    """
    sql = "select id from ps.topics where name = '" + msg.topic + "'"
    cur.execute(sql)
    id_topic = cur.fetchone()
    if not id_topic:
        id_topic = get_last_topic(cur) + 1
        sql = "insert into ps.topics values(" + str(id_topic) + ", '" + msg.topic + "')"
        cur.execute(sql)
        con.commit()
    else:
        id_topic = id_topic[0]
    id = get_last_message(cur)
    id = id + 1
    subs = get_subscribers(cur, id_topic)
    id_pub = msg.node_id
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for sub in subs:
        client = sub[1] + ':' + sub[2]

        if client in CLIENTS:
            msg_new = pickle.dumps(msg)
            udp.sendto(msg_new, (sub[1], int(sub[2])))
        else:
            insert_message(cur, id, msg.content, id_pub, sub[0], id_topic)
    udp.close()

            
def send_message_after_connect(cur, ip_sub, connection):
    """
    Envia para o nó todas as mensagens publicadas nos tópicos assinados por ele enquanto ele estava offline
    :param cur:
    :param ip_sub:
    :param connection:
    :return:
    """
    sql = "select m.id, m.corpo, t.name from ps.messages m join ps.nodes n on m.id_sub = n.id join ps.topics t on m.id_topic = t.id where n.ip = '" + ip_sub + "'"

    cur.execute(sql)
    messages = cur.fetchall()
    if not messages:
        msg = Message('', '', 'Você está atualizado', '')
        msg = pickle.dumps(msg)
        connection.sendall(msg)
    for message in messages:
        try:
            msg = Message(message[0], '', message[1], message[2])
            msg = pickle.dumps(msg)
            connection.sendall(msg)
            sql = "delete from ps.messages where id = "+ str(message[0])
            cur.execute(sql)
            con.commit()
        except:
            print("Cliente desconectado")


# Inicia a conexão e aguarda os nós

ServerSocket = socket.socket()

ThreadCount = 0
clients = {} 

con = connect_database()
cur = con.cursor()
try:
    ServerSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

print('Aguardando conexão...')
ServerSocket.listen(5)

while True:
    Client, address = ServerSocket.accept()
    CLIENTS.append(address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client,))
    ThreadCount += 1

    
ServerSocket.close()
