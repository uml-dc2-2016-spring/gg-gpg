

import os
import lib.config
import lib.util
import lib.server
import lib.sender
import time


if __name__ == "__main__":
    config = lib.config.config() #default .config name

    lib.util.parse_config('.config', os.getcwd())
    while True:
        time.sleep(60)
