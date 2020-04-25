import socket
from message import Message

ClientSocket = socket.socket()
HOST = '127.0.0.1'
PORT = 1233


def publish_message():
    # TODO
    pass

def list_topics():
    # TODO
    pass


def subscribe_topic():
    # TODO
    pass


def unsubscribe_topic():
    # TODO
    pass


FUNCTIONS = {
    '1': publish_message,
    '2': list_topics,
    '3': subscribe_topic,
    '4': unsubscribe_topic,
}

print('Waiting for connection')
try:
    ClientSocket.connect((HOST, PORT))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(1024)

while True:
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