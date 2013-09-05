class Item(object):
    def __init__(self, token):
        self.token = token
        self.items = []
    def push(self, item):
        self.items.append(item)
