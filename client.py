import socket
import pickle
from threading import Timer
from message import Message
import sys, select

ClientSocket = socket.socket()
HOST = '127.0.0.1'
PORT = 1233
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
    string_topic = input("Insert the message topic: ")
    string_msg = input("Insert the message: ")
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
    topic = input("Enter with the Topic ID: ")

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

    topic = input("Enter with the Topic ID: ")

    msg = Message(NODE_ID, 'unsubscribe', topic, topic)
    msg = pickle.dumps(msg)
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)
    print(msg.content)


def broker_connection(node_id):
    print('Waiting for connection')
    try:
        ClientSocket.connect((HOST, PORT))
        ClientSocket.settimeout(0.1)
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
    '2': subscribe_topic,
    '3': unsubscribe_topic,
    '4': publish_message,
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

first = True
while True:
    try:
        Response = ClientSocket.recv(1024)
        Response = pickle.loads(Response)
        print(Response.topic + ': ' + Response.content)
    except:
        pass

    if first:
        menu = 'Select a option: ' \
               '\n 1 - List Topics' \
               '\n 2 - Subscribe Topic' \
               '\n 3 - Unsubscribe Topic' \
               '\n 4 - Publish a message\n'


        print(menu)
        first = False
    action = False
    TIMEOUT = 1
    i, o, e = select.select([sys.stdin], [], [], TIMEOUT)
    # if i:
    #     print("Você digitou: ", sys.stdin.readline().strip())
    # else:
    #     print('Você não digitou nada :(')
    action = sys.stdin.readline().strip()
    if action:
        operation = FUNCTIONS.get(action, False)
        if operation:

            operation()
            first = True
        else:
            print('Invalid command')

ClientSocket.close()