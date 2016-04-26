
import os
import subprocess
import shlex
import re
import socket

def create_channel(name, rootdir, infile=None, outfile='out'):
    """
        params:
            name: a string to name the channel.
            rootdir: the root directory where all channels exist.
            infile: either the name of the fifo to create, or none if the channel is receive only
            outfile: either the name of the text file to create. a text file is always created because either way the sender will save what it sends.

        returns:
            nothing
    """

    name = name.lower()

    cwd = os.getcwd()
    os.chdir(rootdir)

    if not os.path.isdir(name):
        os.mkdir(name)

    os.chdir(name)

    if infile:
        try:
            os.mkfifo(infile)
        except OSError as e:
            if e.errno != 17:
                raise e
            pass
            # if errno 17, file exists, continue as normal and use existing fifo

    # create a blank file to append received messages to
    if outfile:
        open(outfile, 'a').close()

    print 'created channel %s in: %s out: %s' % (name, infile, outfile)

    os.chdir(cwd)

def get_secret_ids():
    """
        List the available secret keys that can be used for decryption or signing.

        return:
            A dictionary containing subkey and key keys, with lists of every available key list respectively

    """
    out = get_output('gpg --list-secret-keys --with-colons').split('\n')

    subkeys = []
    keys = []
    for line in out:
        if re.search('^ssb', line):
            subkeys.append(line.split(':')[4])
        elif re.search('^sec', line):
            keys.append(line.split(':')[4])

    return {'keys': keys, 'subkeys': subkeys }

def get_public_ids():
    """
        Same as get_secret_ids, except for public keys.

        return:
            A dictionary containing subkey and key keys, with lists of each respective available key list.
    """
    out = get_output('gpg --list-keys --with-colons').split('\n')

    keys = []
    subkeys = []

    for line in out:
        if re.search('^pub', line):
            keys.append(line.split(':')[4])
        elif re.search('^sub', line):
            subkeys.append(line.split(':')[4])

    return {'keys': keys, 'subkeys': subkeys }

def resolve_hostname(host, port):
    """
        resolve a domain name (ex. google.com) to an ip address usable with socket.connect()

        params:
            host: the domain name to resolve to an IP address
            port: the port number. this is important because socket.getadddrinfo()
                can return a tuple which is directly passable to socket.connect()

        returns: a tuple for use with socket.connect()
    """
    return socket.getaddrinfo(host, port, 0,0, socket.IPPROTO_TCP)




def run_proc(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0):
    """
        a wrapper around the Popen constructor that calls shlex.split() on the first argument so a single string can be passed instead of a list of strings.

        params: see Popen

        returns: subprocess.Popen object with shlex'ed args.
    """

    args = shlex.split(args)

    return subprocess.Popen(args, bufsize, executable, stdin, stdout, stderr, preexec_fn, close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags)

def get_output(args):
    """
        call subprocess.check_output with shlex'ed args.

        params:
            args: the command to execute

        return:
            the output of the command
    """
    args = shlex.split(args)

    return subprocess.check_output(args)

def encrypt(msg, recipient_ids, sign_id=None, armor=True):
    """
    Encrypt an input string into a gpg message making an external subprocess call to the system's gpg command.

    Raises any exceptions that subprocess.Popen or Popen.communicate might raise.

    params:
        msg: a string to encrypt, in theory should just be a serializable blob but only tested with strings.
        recipient_ids: a list of public keys to encrypt with.
        sign_id: the key ID to sign with.
        armor: flag to tell gpg to generate ascii or binary message

    return: the encrypted string

    """

    cmd = get_encrypt_cmd(recipient_ids, sign_id, armor)

    return run_piped_proc(cmd, msg)

def run_piped_proc(cmd, data):
    """
        pass data to stdin and get the output of the process.

        params:
            cmd: the string to run
            data: the blob to pass to the process over stdin
    """

    p = run_proc(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate(data)

    return out

def recv_ids(keyids):
    """
        request key ids to install from the keyserver. This should be tried if
        gpg cannot decrypt a signed message.

        params:
            keyids: a list of keyids to request from the keyserver.

        return: nothing. throw an exception upon failure.
    """

    cmd = 'gpg --recv-keys '

    for key in keyids:
        cmd += '%s ' % key



def enarmor(msg):
    """
        take a binary gpg message and convert it to an ascii armored one.

        params:
            msg: the binary blob message

        return: the ascii armored message
    """

    cmd = 'gpg --enarmor'

    return run_piped_proc(cmd, msg)

def dearmor(msg):
    """
        convert an ascii armored gpg message to a binary blob.

        params:
            msg: the ascii armored message

        return: the message in binary form
    """

    cmd = 'gpg --dearmor'

    return run_piped_proc(cmd, msg)

def get_encrypt_cmd(recipient_ids, sign_id=None, armor=True):
    """
        create an encrypt/sign command for executing through subprocess.

        the order matters: gpg _options_ (local-user) come before _commands_ (--encrypt)

        params:
            recipient_ids: list of recipient key IDs
            sign_id: optional key ID to sign message with
            armor: flag to tell gpg to generate ascii or binary blob message

        return: the constructed gpg command
    """

    cmd = 'gpg '
    if armor:
        cmd += '--armor '

    if sign_id:
        cmd += '--local-user %s ' % sign_id


    for keyid in recipient_ids:
        cmd += '--recipient %s ' % keyid

    cmd += '--encrypt '

    if sign_id:
        cmd += '--sign '

    return cmd


def get_encrypt_fn(recipient_ids, sign_id=None, armor=True):
    """
        construct and return a method to encrypt messages based on certain keyids. should be passed to a sender as the serializing method.

        params:
            recipient_ids: list of recipient keys to encrypt to
            sign_id: the optional key to sign with.
            armor: flag to
    """

    return (lambda msg: encrypt(msg, keyids, armor))

