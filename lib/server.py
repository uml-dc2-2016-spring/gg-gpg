import SocketServer

import util
import multiprocessing as mp

listening_channels = []

class AppendingTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.

    in handle, implement either append to text file or write new file.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(8193).strip()
        if self.server.deserialize:
            out = self.server.deserialize(self.data)
        out = self.data

        with open(self.server.infile, 'a') as of:
            of.write('%s: %s\n' % (self.client_address[0], out.decode()))


def start_appender(host, port, channel, infile='in', deserializer=None):
    import os
    global listening_channels

    if not os.path.isdir(channel):
       util.create_channel(channel, os.getcwd(), infile)
    os.chdir(channel)

    server = SocketServer.TCPServer((host, port), AppendingTCPHandler)
    server.allow_reuse_address=1
    server.infile = infile
    server.deserialize = deserializer
    server_proc = mp.Process(target=server.serve_forever)
    server_proc.daemon = True
    server_proc.start()
    return server_proc

if __name__ == '__main__':
    import time
    host = 'localhost'
    port = 9000
    channel = 'testin'
    ofile = 'out'

    serv_proc = start_appender(host, port, channel, ofile)

    time.sleep(60)


