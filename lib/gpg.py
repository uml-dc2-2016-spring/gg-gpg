import re
from . import util

def init_gpg_from_config(config):
    """
        wrapper for gpg initialization from config dictionary

        params:
            config: a config dictionary from the config class.

        returns: the gpg object.
    """

    if not 'encrypt_id' in list(config.keys()):
        return None

    recipient_ids = config['encrypt_id'].split(' ')

    sign_id = None
    if 'sign_id' in list(config.keys()):
        sign_id = config['sign_id']

    return gpg(recipient_ids, sign_id)


class gpg(object):
    """
        Class for an interface with command line gpg.
    """

    def __init__(self, recipient_ids, sign_id=None, armor=True):

        self.recipient_ids = recipient_ids
        self.sign_id = sign_id
        self.armor = armor

        self.encrypt_cmd = None
        self.encrypt_cmd = self.set_encrypt_cmd(recipient_ids, sign_id, armor)


    def encrypt(self, msg ):
        """
        Encrypt an input string into a gpg message making an external subprocess call to the system's gpg command.

        Raises any exceptions that subprocess.Popen or Popen.communicate might raise.

        params:
            msg: a string to encrypt, in theory should just be a serializable blob but only tested with strings.

        return: the encrypted string
        """

        return util.run_piped_proc(self.encrypt_cmd, msg)[0]

    def set_encrypt_cmd(self, recipient_ids, sign_id=None,armor=True):
        """
        function to set the encrypted string for an already created gpg instance.

            params:
                recipient_ids: list of new ids. must have at least one.
                sign_id: the key id to sign with.
                armor: the flag to activate the ascii armored output
        """

        if not recipient_ids:
            raise Exception("recipient_ids must be a list containing at least one key id.")

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

        self.encrypt_cmd = cmd

        return cmd

def get_secret_ids():
    """
    List the available secret keys that can be used for decryption or signing.

    return:
        A dictionary containing subkey and key keys, with lists of every available key list respectively

    """
    out = util.get_output('gpg --list-secret-keys --with-colons').split('\n')

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
    List the available secret keys that can be used for decryption or signing.

    return:
        A dictionary containing subkey and key keys, with lists of every available key list respectively

    """
    out = util.get_output('gpg --list-keys --with-colons').split('\n')

    subkeys = []
    keys = []
    for line in out:
        if re.search('^sub', line):
            subkeys.append(line.split(':')[4])
        elif re.search('^pub', line):
            keys.append(line.split(':')[4])

    return {'keys': keys, 'subkeys': subkeys }

def recv_ids(keyids):
    """
    request public key ids to install from the keyserver. This should be tried if
    gpg cannot decrypt a signed message.

    params:
    keyids: a list of keyids to request from the keyserver.

    return: nothing. throw an exception upon failure.
    """

    cmd = 'gpg --recv-keys '

    for key in keyids:
        cmd += '%s ' % key

    util.run_proc(cmd)

def decrypt(msg):
    """
        decrypt a pgp message.

        params:
            msg: the encrypted message

        returns: the stdout result of the call to gpg.
    """

    cmd = 'gpg --decrypt'

    return util.run_piped_proc(cmd, msg)[0]

def get_packet_signer_id(msg):
    """
        get the keyid of the key that signed the message.

        params:
            msg: the signed and not encrypted message.

        returns: the keyid of the signer.
    """

    cmd = 'gpg --list-packets'

    out = util.run_piped_proc(cmd,msg)[0]
