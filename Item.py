class Item(object):
    def __init__(self, email, token):
        self.token = token
        self.items = []
        self.email = email
    def push(self, item):
        self.items.append(item)
