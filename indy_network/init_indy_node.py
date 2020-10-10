import argparse
import os

from plenum.common.constants import CLIENT_STACK_SUFFIX
from plenum.common.keygen_utils import initNodeKeysForBothStacks

from indy_common.config_util import getConfig
from indy_common.config_helper import NodeConfigHelper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate keys for a node's stack"
                    "by taking the node's name and seeds values")
    
    parser.add_argument('--name', required=True, help='node name')
    parser.add_argument('--seed', required=False, type=str,
                        help='seed for keypair')
    parser.add_argument('--force', help='overrides keys', action='store_true')
    args = parser.parse_args()

    print("Node-stack name is", args.name)
    print("Client-stack name is", args.name + CLIENT_STACK_SUFFIX)


    config = getConfig()
    config_helper = NodeConfigHelper(args.name, config)
    os.makedirs(config_helper.keys_dir, exist_ok=True)

    try:
       _, verkey, blskey, key_proof = initNodeKeysForBothStacks(args.name, config_helper.keys_dir, 
                                    args.seed, override=args.force)

       print()
       print("Get your key from here: ")
       print()
       print("Verkey: ")
       print(verkey)
       print("BLS: ")
       print(blskey)
       print("key_proof")
       print(key_proof)

    except Exception as ex:
        print(ex)
        exit()
