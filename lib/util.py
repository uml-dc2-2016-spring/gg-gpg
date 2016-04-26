
import os
import subprocess as sp
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

    if outfile:
        try:
            os.mkfifo(outfile)
        except OSError as e:
            if e.errno != 17:
                raise e
            pass
            # if errno 17, file exists, continue as normal and use existing fifo

    # create a blank file to append received messages to
    if infile:
        open(infile, 'a').close()

    os.chdir(cwd)

def open_fifo_read(name, root=None):
    return open_fifo(name, root, 'r')

def open_fifo_write(name, root=None):
    return open_fifo(name, root, 'w')

def open_fifo(name, root, mode, buffering=-1):
    if root:
        name = os.path.join(root, name)

    return open(name, mode, buffering)

def resolve_hostname(host, port):
    return socket.getaddrinfo(host, port, 0,0, socket.IPPROTO_TCP)

def get_secret_keys():
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

def get_public_keys():
    """
        Same as get_secret_keys, except for public keys.

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


def run_proc(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0):
    """
        a wrapper around the Popen constructor that calls shlex.split() on the first argument so a single string can be passed instead of a list of strings.

        params: see Popen

        returns: subprocess.Popen object with shlex'ed args.
    """

    args = shlex.split(args)

    return sp.Popen(args, bufsize, executable, stdin, stdout, stderr, preexec_fn, close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags)

def get_output(args):
    """
        call subprocess.check_output with shlex'ed args.

        params:
            args: the command to execute

        return:
            the output of the command
    """
    args = shlex.split(args)

    return sp.check_output(args)

def encrypt(msg, recipient_ids, armor=True):
    """
    Encrypt an input string into a gpg message making an external subprocess call to the system's gpg command.

    Raises any exceptions that subprocess.Popen or Popen.communicate might raise.

    params:
        `msg`: a string to encrypt, in theory should just be a serializable blob but only tested with strings.

    return: the encrypted string

    """

    cmd = 'gpg --encrypt '

    if armor:
        cmd += '--armor '

    for keyid in recipient_ids:
        cmd += '--recipient '
        cmd += keyid
        cmd += ' '

    return run_piped_proc(cmd, msg)

def run_piped_proc(cmd, data):
    """
        pass data to stdin and get the output of the process.
    """

    p = run_proc(cmd, stdin=sp.PIPE, stdout=sp.PIPE)
    out, err = p.communicate(data)

    return out


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

