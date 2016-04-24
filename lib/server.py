import SocketServer

import util

channels = []

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(8193).strip()
        out = util.run_piped_proc('gpg --quiet --decrypt', self.data)
        with open("server.log", "a") as log:
            log.write("{}: {}\n".format(self.client_address[0], out.decode()))


def start_server(host, port, channel):
    global channels

    os.chdir(channel)
    channels.append(channel)

    server = SocketServer.TCPServer((host, port), MyTCPHander)
    server.allow_reuse_address=1
    server_proc = mp.Process(target=server.serve_forever)
    server_proc.daemon = True
    server_proc.start()
    return server_proc

