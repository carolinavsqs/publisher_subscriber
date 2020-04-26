import socket
import pickle
from message import Message

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
    # TODO
    pass

def list_topics():
    """

    :return: List of topics available to subscribe
    """
    msg = pickle.dumps(Message(NODE_ID, 'list', ''))
    ClientSocket.send(msg)

    msg = ClientSocket.recv(2048)
    msg = pickle.loads(msg)
    print(msg.content)

    return True


def subscribe_topic():
    # TODO
    pass


def unsubscribe_topic():
    # TODO
    pass


def broker_connection(node_id):
    print('Waiting for connection')
    try:
        ClientSocket.connect((HOST, PORT))
    except socket.error as e:
        print(str(e))

    msg = pickle.dumps(Message(node_id, 'connect', ''))
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

while True:
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    menu = 'Select a option: ' \
           '\n 1 - List Topics' \
           '\n 2 - Subscribe Topic' \
           '\n 3 - Unsubscribe Topic' \
           '\n 4 - Publish a message\n'
    action = input(menu)
    operation = FUNCTIONS.get(action, False)

    if operation:
        operation()
    else:
        print('Invalid command')

ClientSocket.close()