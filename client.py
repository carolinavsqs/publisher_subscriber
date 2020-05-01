import socket
import pickle
from _thread import *
from message import Message

ClientSocket = socket.socket()
HOST = '127.0.0.1'
PORT = 1232
NODE_ID = ''


def load_node_id():
    try:
        file = open("id.txt", "r")
        node_id = file.readline()
        return node_id
        file.close()
    except:
        return False



def save_node_id(node_id):
    file = open("id.txt", "w")
    file.write(str(node_id))
    file.close()


def publish_message():
    string_topic = input("Insira o tópico da mensagem: ")
    string_msg = input("Insira a mensagem: ")
    msg = pickle.dumps(Message(NODE_ID, 'publish', string_msg, string_topic))
    ClientSocket.send(msg)

def list_topics():
    """

    :return: List of topics available to subscribe
    """
    msg = pickle.dumps(Message(NODE_ID, 'list_all', '', ''))
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)
    print(msg.content)

    return True


def subscribe_topic():
    topic = input("Insira o número do tópico: ")

    msg = Message(NODE_ID, 'subscribe', topic, topic)
    msg = pickle.dumps(msg)
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)
    print(msg.content)


def unsubscribe_topic():
    msg = Message(NODE_ID, 'list_subscribed', '', '')
    msg = pickle.dumps(msg)
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)
    print(msg.content)

    if msg.topic:
        topic = input("Insira o número do tópico: ")

        msg = Message(NODE_ID, 'unsubscribe', topic, topic)
        msg = pickle.dumps(msg)
        ClientSocket.send(msg)

        msg = ClientSocket.recv(2048)
        msg = pickle.loads(msg)
        print(msg.content)

def get_subscribed_topics():
    msg = Message(NODE_ID, 'list_subscribed', '', '')
    msg = pickle.dumps(msg)
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)
    print(msg.content)


def broker_connection(node_id):
    print('Aguardando conexão...')
    try:
        ClientSocket.connect((HOST, PORT))
    except socket.error as e:
        print(str(e))

    msg = pickle.dumps(Message(node_id, 'connect', '', ''))
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)

    if msg.message_type == "connect":
        NODE_ID = msg.node_id
        save_node_id(NODE_ID)
        print(msg.content)
    else:
        print(msg.content)


FUNCTIONS = {
    '1': list_topics,
    '2': get_subscribed_topics,
    '3': subscribe_topic,
    '4': unsubscribe_topic,
    '5': publish_message,
}


NODE_ID = load_node_id()
broker_connection(NODE_ID)


# data = b""
# while True:
#     packet = ClientSocket.recv(4096)
#     print(packet)
#     if not packet: break
#     data += packet

# Response = ClientSocket.recv(1024)
# Response = pickle.loads(Response)
# print(Response.topic + ': ' + Response.content)


def threaded_message(ClientSocket):
    HOST = ''  # Endereco IP do Servidor
    PORT = ClientSocket.getsockname()[1]  # Porta que o Servidor esta
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    orig = (HOST, PORT)
    udp.bind(orig)

    while True:
        Response = udp.recv(1024)
        Response = pickle.loads(Response)
        print(Response.topic + ': ' + Response.content)

Response = ClientSocket.recv(1024)
Response = pickle.loads(Response)
print(Response.topic + ': ' + Response.content)

start_new_thread(threaded_message, (ClientSocket,))
while True:

    menu = '\n --------------------' \
           '\n O que você gostaria de fazer? ' \
           '\n 1 - Ver todos os tópicos' \
           '\n 2 - Ver tópicos em que você está inscrito(a)' \
           '\n 3 - Inscrever-se em um tópico' \
           '\n 4 - Cancelar inscrição em um tópico' \
           '\n 5 - Publicar uma mensagem\n'

    action = input(menu)

    if action:
        operation = FUNCTIONS.get(action, False)
        if operation:

            operation()
            first = True
        else:
            print('Comando inválido!')

ClientSocket.close()
