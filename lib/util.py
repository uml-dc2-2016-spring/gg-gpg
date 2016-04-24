
import os
import subprocess as sp
import shlex
import re

def create_channel(name, rootdir, infile='in', outfile='out'):
    """
        Create the fifo and text file objects that will be written to and read from by the end user. If the directory doesn't exist, create that too.

        params:
            name: a string to name the channel.
            rootdir: the root directory where all channels exist.

        returns:
            nothing
    """

    name = name.lower()

    cwd = os.getcwd()
    os.chdir(rootdir)

    if not os.path.isdir(name):
        os.mkdir(name)

    os.chdir(name)

    os.mkfifo(infile)
    open(outfile, 'a+')

    os.chdir(cwd)

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

