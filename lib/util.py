
import os
import subprocess
import shlex
import re
import socket
import config
import logging
import server
import sender
import gpg

def parse_config(filename, rootdir=None):
    """
        open and parse the starting config file. create the channels based on the config file.

        will use the current working directory as the rootdir if none is found.

        params:
            filename: the config file's filename.
            rootdir: a path to the directory with the config file.
    """

    cwd = os.getcwd()

    if not rootdir:
        rootdir = cwd

    os.chdir(rootdir)

    cfg = config.config(filename, rootdir)

    channels = cfg.get_channel_list()

    procs = {}

    for chan in channels:

        opts = cfg.get_channel_opts(chan)
        procs[chan] = get_server_sender_procs(chan, opts)


    os.chdir(cwd)

def get_server_sender_procs(name, opts):
    """
        parse an individual channel's options and create processes for each
        channel's sender and server

        params:
            opts: the dictionary of channel options.

        returns:
            nothing. will raise an exception if it fails.
    """

    gpg_helper = gpg.init_gpg_from_config(opts)

    deserializer = None
    sender_proc = None

    serializer = lambda x: gpg_helper.encrypt(x)

    #if the store_raw key is not present, attempt to decrypt the data.
    if not 'store_raw' in opts.keys():
        deserializer = lambda x: gpg.decrypt(x)

    # create the channel. none can be passed into root because we are assuming correct directory.
    create_channel(name, os.getcwd(), infile='in', outfile='out')

    cwd = os.getcwd()
    os.chdir(name)

    server_proc = server.init_server_from_config(name, opts, deserializer=deserializer)
    sender_proc = sender.init_sender_from_config(opts)

    if server_proc:
        server_proc.start()
    if sender_proc:
        sender_proc.start()

    os.chdir(cwd)

    return (server_proc, sender_proc)

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

    os.chdir(cwd)

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

def run_piped_proc(cmd, data):
    """
        pass data to stdin and get the output of the process.

        params:
            cmd: the string to run
            data: the blob to pass to the process over stdin
    """

    p = run_proc(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate(data)

    return out, err
