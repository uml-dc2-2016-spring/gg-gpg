
import os

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

