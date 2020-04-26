class Message:
    message_type = ''
    node_id = ''
    topic = ''
    content = ''

    def __init__(self, node_id, message_type, content):
        self.node_id = node_id
        self.message_type = message_type
        self.content = content


'''
    Types:
        - connect
        - publish
        - list
        - subscribe
        - unsubscribe
'''