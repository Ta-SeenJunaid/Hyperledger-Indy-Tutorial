#source https://github.com/hyperledger/indy-node/blob/master/scripts/

import argparse



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