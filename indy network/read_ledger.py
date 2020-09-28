#source https://github.com/hyperledger/indy-node/blob/master/scripts/read_ledger

import argparse
import logging
import os

from indy_common.config_util import getConfig

logging.root.handlers = []
logger = logging.getLogger()
logger.propagate = False
logger.disabled = True
_DATA = 'data'

# TODO: Replace with constant from config
postfix = '_transactions'



def read_args():
    parser = argparse.ArgumentParser(
        description="Read ledger transactions")

    parser.add_argument('--type', required=True,
                        help='Ledger type (pool, domain, config)')
    parser.add_argument(
        '--frm',
        required=False,
        default=None,
        help="read all transactions starting from (beginning by default)")
    parser.add_argument('--to', required=False, default=100,
                        help="read all transactions till (100 by default)")
    parser.add_argument('--seq_no', required=False,
                        help="read a particular transaction")
    parser.add_argument('--count', required=False, action='store_true',
                        help="returns the number of txns in the given ledger")
    parser.add_argument('--node_name', required=False, help="Node's name")
    parser.add_argument('--serializer', required=False, default='json',
                        help="How to represent the data (json by default)")
    parser.add_argument('--network', required=False, type=str,
                        help="Network name to read ledger from")

    return parser.parse_args()

def get_ledger_dir(node_name, network):
    config = getConfig()
    _network = network if network else config.NETWORK_NAME
    ledger_base_dir = config.LEDGER_DIR
    if node_name:
        # Build path to data if --node_name was specified
        ledger_data_dir = os.path.join(ledger_base_dir, _network, _DATA, node_name)
    else:
        ledger_data_dir = os.path.join(ledger_base_dir, _network, _DATA)
        if os.path.exists(ledger_data_dir):
            dirs = os.listdir(ledger_data_dir)
            if len(dirs) == 0:
                print("Node's 'data' folder not found: {}".format(ledger_data_dir))
                exit()
            # --node_name parameter was not set, therefore we can choose first Node name in data dir
            ledger_data_dir = os.path.join(ledger_data_dir, dirs[0])
    if not os.path.exists(ledger_data_dir):
        print("No such file or directory: {}".format(ledger_data_dir))
        print("Please check, that network: '{}' was used ".format(_network))
        exit()

    return ledger_data_dir