import SocketServer
import os
import multiprocessing
import tempfile
import datetime
import socket
import sys
import time

import util
import gpg

class AbstractTCPHandler(SocketServer.BaseRequestHandler):
    """
        class for shared methods between appending and separate file tcp handlers.
    """
    def recv_timeout(self, the_socket,timeout=2):
        #make socket non blocking
        the_socket.setblocking(0)

        #total data partwise in an array
        total_data=[];
        data='';

        #beginning time
        begin=time.time()
        while 1:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break

                #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break

                #recv something
            try:
                data = the_socket.recv(8192)
                if data:
                    total_data.append(data)
                    #change the beginning time for measurement
                    begin=time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        the_socket.setblocking(1)
        return ''.join(total_data)

    def recv_all_tmp_file(self):
        """
            receive all data and write it to a temporary file.

            return: the temporary file containing the read socket.
        """
        tmp = tempfile.TemporaryFile()

        data = self.recv_timeout(self.request)
        tmp.write(data)

        tmp.seek(0)

        return tmp

    def deserialize(self, data):
        if self.server.deserializer:
            return self.server.deserializer(data)
        return data



class AppendingTCPHandler(AbstractTCPHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.

    in handle, implement either append to text file or write new file.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        with self.recv_all_tmp_file() as tmp:

            data = tmp.read()
            print data

            data = self.deserialize(data)

            name = self.client_address[0] # set name to IP address first

            uid = gpg.get_packet_signer_id(data)

            time = datetime.datetime.now().strftime('%c')

            with open(self.server.outfile, 'a') as of:
                of.write('%s %s: %s\n' % (time, name, data.decode()))


class SeparateFileTCPHandler(AbstractTCPHandler):
    """
        The connection handler for the server.

        This one implements separate file saving per connection.
    """
    def handle(self):
        with self.recv_all_tmp_file() as tmp:
            data = tmp.read()

            data = self.deserialize(data)

            filename = datetime.datetime.now().strftime('%Y%b%d_%H_%M_%S_%f')

            #TODO test what happens if file already exists, add try/except block
            with open(filename, 'wb') as f:
                f.write(data)

def init_server_from_config(name, config, outfile='out', deserializer=None):
    """
        initialize the server based on the config dictionary.

        see init_server
    """
    if 'file_save' in config.keys():
        return init_server(name, config, SeparateFileTCPHandler, outfile, deserializer)
    else:
        return init_server(name, config, AppendingTCPHandler, outfile, deserializer)

def init_server(name,  config, TCPHandler, outfile='out', deserializer=None):
    """
        Initialize but do not start a log appending server.

        params:
            name: the channel name.
            config: a dictionary generated from a config file.
            TCPHandler: the tcp handler class the server calls when connected
            outfile: the file to write received data to.
            deserializer: the method to call to deserialize data.

        return: A multiprocessing.Process, targetting the server.
    """
    if not 'incoming_port' in config.keys():
        return None


    # bind to all interfaces for listening.
    host = '0.0.0.0'
    port = int(config['incoming_port'])

    listener = SocketServer.TCPServer((host, port), TCPHandler)
    listener.allow_reuse_address=1 # in case server needs to be stopped and started.
    listener.outfile = os.path.join(os.getcwd(), outfile) # for the handler to see.
    listener.deserializer = deserializer
    def start():
        print 'starting server on port %s' % port
        listener.serve_forever()

    proc = multiprocessing.Process(target=start)
    proc.daemon = True # this python process will try to clean up the server's process at exit.

    return proc
