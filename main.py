
import subprocess
import SocketServer
import multiprocessing as mp

import socket
import sys

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
        gpg = subprocess.Popen(["gpg", "--quiet", "--decrypt"], stdin= subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = gpg.communicate(input = self.data)
        with open("server.log", "a") as log:
            log.write("{}: {}\n".format(self.client_address[0], out.decode()))


def try_connect(addrinfoList):
    """
    Tries to connect to the list of addrinfo objects passed to it.

    If successful, returns a connected TCP socket.

    Upon failure raises an Exception.

    Parameters:

    - `addrinfoList` the list of addrinfo objects, which should be the result of socket.getaddrinfo() or similar methods.

    """
    

    addrinfoList:
    for ftpca in addrinfoList:
        sock=socket.socket(*ftpca[0:3])
        rc = sock.connect_ex(ftpca[4])
        if rc == 0:
            return sock
    raise Exception("could not construct socket from addrinfo")

def encrypt(msg):
    """
    Encrypt an input string into a gpg message making an external subprocess call to the system's gpg command.

    Returns the encrypted string.

    Raises any exceptions that subprocess.Popen or Popen.communicate might raise.

    Parameters:

    - `msg`: a string to encrypt, in theory should just be a serializable blob but only tested with strings.


    """
    gpg = subprocess.Popen(["gpg", "--armor", "--encrypt", "--recipient", "89DED062845500B7", "--recipient", "mattwollf@gmail.com"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
    out, err = gpg.communicate(input=msg)
    return out.decode()



if __name__ == "__main__":
    HOST, PORT = 'localhost', int(raw_input("server port: "))
    # Create the server, binding to localhost on port 9999

    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    # Fast starting/stopping of server can cause port to block.
    #
    server.allow_reuse_address=1

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server_proc = mp.Process(target=server.serve_forever)
    server_proc.daemon = True

    server_proc.start()

    HOST, PORT = raw_input("Hostname/IP: "),int(raw_input("port number: "))

    # Create a socket (SOCK_STREAM means a TCP socket)

    addrinfo = socket.getaddrinfo(HOST, PORT)


    while True:
        try:
            sock = try_connect(addrinfo)
            # Connect to server and send data
            msg = raw_input("> ")
            xfer = encrypt(msg)
            sock.sendall(xfer)

            # Receive data from the server and shut down
        except socket.error as e:
            print e
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()


