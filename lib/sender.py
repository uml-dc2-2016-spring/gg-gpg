
import socket
import util
import time
import gpg
import multiprocessing
import os
import sys

def init_sender_from_config(config):
    """
        alternative constructor wrapper which creates the sender object from a dictionary returned by a config instance's get_channel_opts() method

        raises an exception if one needed key is not present in the dictionary.

        params:
            config: a dictionary with the sender settings

        return: a properly initialized sender object.

    """
    if config.has_key('remote_host') != config.has_key('outgoing_port'):
        raise Exception("malformed config file. sender needs both remote_host and outgoing_port values")

    elif not (config.has_key('remote_host') and config.has_key('outgoing_port')):
        return None

    sign_id = None
    encrypt_ids = None
    host = config['remote_host']
    port = int(config['outgoing_port'])

    if config.has_key('sign_id'):
        sign_id = config['sign_id']

    if config.has_key('encrypt_id'):
        encrypt_ids = config['encrypt_id'].split()

    gpg_helper = gpg.init_gpg_from_config(config)

    serializer = None
    if encrypt_ids:
        print 'creating a serializer for encrypted data'
        serializer = lambda x: gpg_helper.encrypt(x)

    sender = init_appending_sender('in', 'out',None, host, port, serializer)

    proc = multiprocessing.Process(target=sender.start)
    proc.daemon = True

    return proc


def init_noappend_sender(fifoname, rootdir, host, port, serializer=None):
    return sender(fifoname, None, rootdir, host, port, serializer)

def init_appending_sender(fifoname, log, rootdir, host, port, serializer=None):
    return sender(fifoname, log, rootdir, host, port, serializer)

class sender:

    def __init__(self, fifoname, log, rootdir, host, port, serializer=None):
        """
        params:
            fifoname: name of the fifo file to listen to
            log: the local text file to append sent messages to.
            rootdir: root channel directory.
            host: remote host to send to
            port: port on remote host
            serializer: function that prepares received data for transfer. if None, data is sent as is.

        """
        if not rootdir:
            rootdir = os.getcwd()
        self.log = log
        self.rootdir = rootdir
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fifo = os.path.join(rootdir, fifoname)
        self.serialize = serializer

    def start(self):
        while True:
            data = None
            with open(self.fifo, 'r', 1) as f:

                data = f.read()

            if self.log:
                with open(self.log, 'a') as f:

                    localtime = time.asctime( time.localtime(time.time()) )
                    f.write('%s sent: %s' % (localtime, data))

            if self.serialize:
                data = self.serialize(data)[0]

            self.sock.connect((self.host, self.port))
            print 'sending to %s' % self.port
            sys.stdout.flush()
            self.sock.send(data)
            self.sock.close()
            print 'sender socket closed'
            sys.stdout.flush()


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
