import threading, pymongo
import Queue
import socket
import pickle
import StringIO
import dropbox
import urllib2

class ThreadWork(threading.Thread):
    """ Work thread """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            item = self.queue.get()
            self.process(item)
            self.queue.task_done()
    def process(self, item):
        print item.token
        dropb = dropbox.client.DropboxClient(item.token)
        for i in item.items:
            img = urllib2.urlopen(i[1]).read()
            try:
                dropb.put_file(i[0], img)
            except dropbox.rest.ErrorResponse as e:
                if e.status == 401:
                    conn = pymongo.Connection("localhost", 27017)
                    db = conn["saver1024"]
                    u = db["users"].find_one({"email":item.email})
                    if u.has_key("token"):
                        u.pop("token")
                    db["users"].save(u)
                    conn.close()
                    print "The user have deauthorised the access."
                    break

class Server():
    """ serve for the coming download """
    def __init__(self, queue, host = "localhost", port = 1024):
        self.queue = queue
        self.host = host
        self.port = port
    def handle(self, conn, address):
        """   """
        print "Conncetion from %s" % str(address)
        msg = ""
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            msg += chunk
        conn.close()
        print "Disconnect with %s" % str(address)
        item = pickle.loads(msg)
        self.queue.put(item)
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        while True:
            (clientsocket, address) = s.accept()
            self.handle(clientsocket, address)

def main():
    queue = Queue.Queue()
    for i in range(5):
        t = ThreadWork(queue)
        t.start()
    server = Server(queue, "localhost", 1024)
    server.run()

if __name__ == "__main__":
    main()
