
import socket
import util
import time

def init_noappend_sender(fifoname, root, host, port, serializer=None):
    return sender(fifoname, None, root, host, port, serializer)

def init_appending_sender(fifoname, log, root, host, port, serializer=None):
    return sender(fifoname, log, root, host, port, serializer)

class sender:

    def __init__(self, fifoname, log, root, host, port, serializer=None):
        """
        params:
            fifoname: name of the fifo file to listen to
            log: the local text file to append sent messages to.
            root: root channel directory.
            host: remote host to send to
            port: port on remote host
            serializer: function that prepares received data for transfer. if None, data is sent as is.

        """
        if not root:
            root = os.getcwd()
        self.log = log
        self.root = root
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fifo = os.path.join(root, fifoname)
        self.serialize = serializer

    def start(self):
        while True:
            with open(self.fifo, 'r') as f:

                data = f.read()
                if self.log:
                    with open(self.log, 'a') as f:

                        localtime = time.asctime( time.localtime(time.time()) )
                        f.write('%s sent: %s' % (localtime, data))

                if self.serialize:
                    data = self.serialize(f.read())

                self.sock.connect((host, port))
                self.sock.send(data)
                self.sock.close()

    def __str__(self):
        return str(name) + ':' + str(host) + ':' + str(port)

    def __eq__(self, other):

        preds = []
        preds.append(self.name == other.name)
        preds.append(self.host == other.host)
        preds.append(self.port == other.port)

        return all(preds)

    def __ne__(self, other):
        return not self.__eq__(other)

if __name__ == '__main__':
    import os
    infile = None
    outfile = 'out'
    root = os.getcwd()
    channel = 'testout'

    host = '127.0.0.1'
    port = 9000

    util.create_channel(channel, root, infile, outfile)
    sender = sender(outfile, os.path.join(root, channel) , host, port)
    sender.start()
