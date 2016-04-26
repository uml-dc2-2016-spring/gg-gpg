
import socket
import util
import time

def init_sender_from_config_dict(config):
    """
        alternative constructor wrapper which creates the sender object from a dictionary returned by a config instance's get_channel_opts() method

        raises an exception if one or more needed key is not present in the dictionary.

        params:
            config: a dictionary with the sender settings

        return: a properly initialized sender object.

    """
    if not (config.has_key('remote_host') and onfig.has_key('outgoing_port')):
        raise Exception('Malformed config file. For an outgoing connection, both remote_host and outgoing_port must be set in the config file.')

    sign_id = None
    encrypt_ids = None
    host = config['remote_host']
    port = config['outgoing_port']

    if config.has_key('sign_id'):
        sign_id = config['sign_id']

    if config.has_key('encrypt_id'):
        encrypt_ids = config['encrypt_id'].split()

    serializer = util.get_encrypt_fn(encrypt_ids, sign_id)

    return init_appending_sender('in', 'out',None, host, port, serlializer)


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
            with open(self.fifo, 'r') as f:

                data = f.read()
                if self.log:
                    with open(self.log, 'a') as f:

                        localtime = time.asctime( time.localtime(time.time()) )
                        f.write('%s sent: %s' % (localtime, data))

                if self.serialize:
                    data = self.serialize(data)

                print host, port
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
    infile = 'in'
    outfile = 'out'
    rootdir = os.getcwd()
    channel = 'testout'

    host = 'localhost'
    port = 9000

    util.create_channel(channel, rootdir, infile, outfile)
    sender = sender(infile, outfile, os.path.join(rootdir, channel) , host, port)
    sender.start()
