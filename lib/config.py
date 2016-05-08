
import configparser
import os

class config(object):

    def __init__(self, name='.config', root=None):
        self.config = configparser.SafeConfigParser(allow_no_value=True)
        if root:
            name = os.path.join(root, name)
        self.config_file = name

        self.config.read(name)

    def get_channel_list(self):
        return self.config.sections()

    def get_channel_opts(self, channel):
        return dict(self.config.items(channel))

    def __str__(self):

        with open(self.config_file, 'r') as f:
            data = f.read()
        return data

    def __eq__(self, other):

        return self.__str__() == other.__str__()

    def __ne__(self, other):

        return not self.__eq__(other)
