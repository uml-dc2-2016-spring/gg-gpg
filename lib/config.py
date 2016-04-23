
import ConfigParser
import os

def parse_file(name, root=None):
    config = ConfigParser.SafeConfigParser(allow_no_value=True)

    if root:
        name = os.path.join(root, name)

    config.read(name)
    return config

def get_channel_list(config=None):

    if not config:
        config = parse_file('.config')

    return config.sections()

