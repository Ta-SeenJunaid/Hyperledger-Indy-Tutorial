import argparse
from collections import namedtuple
import fileinput
import ipaddress
import os


from common.exceptions import PlenumValueError
from ledger.genesis_txn.genesis_txn_file_util import create_genesis_txn_init_ledger


from plenum.common.config_helper import PConfigHelper, PNodeConfigHelper
from plenum.common.member.steward import Steward
from plenum.common.util import hexToFriendly, is_hostname_valid

from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper, NodeConfigHelper

CLIENT_CONNECTIONS_LIMIT = 500


class PoolLedger:

    @staticmethod
    def _bootstrap_args_type_ips_hosts(ips_hosts_str_arg):
        ips = []
        for arg in ips_hosts_str_arg.split(','):
            arg = arg.strip()
            try:
                ipaddress.ip_address(arg)
            except ValueError:
                if not is_hostname_valid(arg):
                    raise argparse.ArgumentTypeError(
                    "'{}' is not a valid IP or hostname".format(arg)
                )
                else:
                    ips.append(arg)
            else:
                ips.append(arg)

        return ips

    @staticmethod
    def _bootstrap_args_type_verkeys(verkeys_str_arg):
        verkeys = []
        i =1 
        for arg in verkeys_str_arg.split(','):
            arg = str(arg)
            arg = arg.strip()
            if len(arg) != 64:
                raise argparse.ArgumentTypeError("The lenght verification key {} should be 64 digit long".format(i))           
            verkeys.append(arg)
            i += 1

        return verkeys

    
    @staticmethod
    def _bootstrap_args_type_bls(bls_str_arg):
        bls = []
        i =1 
        for arg in bls_str_arg.split(','):
            arg = str(arg)
            arg = arg.strip()
            if len(arg) != 174:
                raise argparse.ArgumentTypeError("The lenght of this key {} should be 174 digit long".format(i))           
            bls.append(arg)
            i += 1

        return bls

    @staticmethod
    def _bootstrap_args_type_list(list_str_arg):
        arg_list = []
        i =1 
        for arg in list_str_arg.split(','):
            arg = str(arg)
            arg = arg.strip()
            arg_list.append(arg)
            i += 1

        return arg_list

    @staticmethod
    def _bootstrap_args_type_port(port_str_arg):
        arg_list = []
        i =1 
        for arg in port_str_arg.split(','):
            arg = str(arg)
            arg = arg.strip()
            try:
                arg_list.append(int(arg))
            except Exception as ex:
                print("Port must be an integer")
                print(ex)
                exit()
            i += 1

        return arg_list


    @staticmethod
    def _bootstrap_args_type_dids(dids_str_arg):
        did = []
        i =1 
        for arg in dids_str_arg.split(','):
            arg = str(arg)
            arg = arg.strip()
            if len(arg) != 22:
                raise argparse.ArgumentTypeError("The lenght of did {} should be 22 digit long".format(i))           
            did.append(arg)
            i += 1

        return did


    @classmethod 
    def gen_node_def(cls, names, ips, node_ports, client_ports, 
                    blskeys, bls_proofs, verkeys, steward_nyms):

        node_count = len(names)

        if not ips:
            ips = ['127.0.0.1'] * node_count
        else:
            if len(ips) != node_count:
                if len(ips) > node_count:
                    ips = ips[:node_count]
                else:
                    ips += ['127.0.0.1'] * (node_count - len(ips))

        node_defs = []
        for i in range(1, node_count + 1):
            node_defs.append(NodeDef(
                name=names[i-1],
                ip=ips[i-1],
                node_port=node_ports[i-1],
                client_port=client_ports[i-1],
                idx=i,
                verkey=verkeys[i-1],
                blskey=blskeys[i-1],
                bls_proof=bls_proofs[i-1],
                steward_nym=steward_nyms[i-1]))

        return node_defs


    @classmethod 
    def init_pool_ledger(cls, appendToLedgers, genesis_dir, config):
        pool_txn_file = cls.pool_ledger_file_name(config)
        pool_ledger = create_genesis_txn_init_ledger(genesis_dir, pool_txn_file)
        if not appendToLedgers:
            pool_ledger.reset()
        return pool_ledger


    @classmethod
    def pool_ledger_file_name(cls, config):
        return config.poolTransactionsFile


    @staticmethod
    def write_node_params_file(filePath, name, nIp, nPort, cIp, cPort):
        contents = [
            'NODE_NAME={}'.format(name),
            'NODE_IP={}'.format(nIp),
            'NODE_PORT={}'.format(nPort),
            'NODE_CLIENT_IP={}'.format(cIp),
            'NODE_CLIENT_PORT={}'.format(cPort),
            'CLIENT_CONNECTIONS_LIMIT={}'.format(CLIENT_CONNECTIONS_LIMIT)
        ]
        with open(filePath, 'w') as f:
            f.writelines(os.linesep.join(contents))   

    @staticmethod
    def get_nym_from_verkey(verkey: bytes):
        return hexToFriendly(verkey) 

    @classmethod
    def bootstrap_pool_ledger(cls, config, nodeParamsFileName, config_helper_class=PConfigHelper,
                              node_config_helper_class=PNodeConfigHelper,
                             chroot: str=None):
        parser = argparse.ArgumentParser(description="Generate pool transactions")
        parser.add_argument('--nodeVerkeys', required=True,
                            help='Node Verkey, provide comma separated verification keys',
                            type=cls. _bootstrap_args_type_verkeys)
        parser.add_argument('--nodeBlskeys', required=True,
                            help='Node BLS keys, provide comma separated Bls keys',
                            type=cls. _bootstrap_args_type_bls)
        parser.add_argument('--nodeBlsProofs', required=True,
                            help='Node Proof of possession for BLS key, provide comma separated proof',
                            type=cls. _bootstrap_args_type_bls)
        parser.add_argument('--nodeName', required=True,
                            help='Node name, provide comma separated name',
                            type=cls. _bootstrap_args_type_list)
        parser.add_argument('--nodePort', required=True,
                            help='Node port, provide comma separated port',
                            type=cls._bootstrap_args_type_port)
        parser.add_argument('--clientPort', required=True,
                            help='Client port, provide comma separated port',
                            type=cls._bootstrap_args_type_port)
        parser.add_argument('--stewardDids', required=True,
                            help='Stewards Dids, provide comma separated dids',
                            type=cls._bootstrap_args_type_dids)
        parser.add_argument('--nodeNum', type=int, nargs='+',
                            help='the number of the node that will '
                                 'run on this machine')
        parser.add_argument('--ips',
                            help='IPs/hostnames of the nodes, provide comma '
                                  'separated IPs, if no of IPS provided are less than number of nodes then the remaining'
                                  'nodes are assigned the loopback IP, '
                                  'i.e 127.0.0.1',
                            type=cls._bootstrap_args_type_ips_hosts)
        parser.add_argument('--network', required=False,
                            help='Network name (default sandbox)',
                            type=str,               
                            default="sandbox")
        parser.add_argument(
            '--appendToLedgers',
            help="Determine if ledger files needs to be erased "
                 "before writing new information or not",
            action='store_true')  

        args = parser.parse_args()


        if ((len(args.nodeName) != len(args.nodeVerkeys)) or 
        (len(args.nodeBlskeys) != len(args.nodeVerkeys)) or 
        (len(args.nodeBlskeys) != len(args.nodeBlsProofs)) or
        (len(args.nodePort) != len(args.nodeBlsProofs)) or
        (len(args.nodePort) != len(args.clientPort)) or
        (len(args.stewardDids) != len(args.clientPort))):
            raise argparse.ArgumentTypeError("Some arguments are missing.")


        if isinstance(args.nodeNum, int):
            if not (1 <= args.nodeNum <= len(args.nodeName)):
                raise PlenumValueError(
                    'args.nodeNum', args.nodeNum,
                    ">= 1 && <= len(args.nodeName) {}".format(len(args.nodeName))
                )
        elif isinstance(args.nodeNum, list):
            if any([True for x in args.nodeNum if not ( 1 <= x <= len(args.nodeName))]):
                raise PlenumValueError(
                    'some items in nodeNum list', args.nodeNum,
                    ">=1 && <= len(args.nodeName) {}".format(len(args.nodeName))  
            ) 

        node_num = [args.nodeNum, None] if args.nodeNum else [None]

        node_defs = cls.gen_node_def(args.nodeName, args.ips, args.nodePort, args.clientPort,
                                        args.nodeBlskeys, args.nodeBlsProofs,  args.nodeVerkeys,
                                        args.stewardDids)

        if args.nodeNum:

            for line in fileinput.input(['/etc/indy/indy_config.py'], inplace=True):
                if 'NETWORK_NAME' not in line:
                    print(line, end="")
            with open('/etc/indy/indy_config.py', 'a') as cfgfile:
                cfgfile.write("NETWORK_NAME = '{}'".format(args.network))

        for n_num in node_num:
            cls.bootstrap_pool_ledger_core(config, args.network, args.appendToLedgers, node_defs, 
                                    n_num, nodeParamsFileName, config_helper_class, 
                                    node_config_helper_class) 

    @classmethod 
    def bootstrap_pool_ledger_core(
             cls,
            config,
            network,
            appendToLedgers,
            node_defs,
            localNodes,
            nodeParamsFileName,
            config_helper_class=PConfigHelper,
            node_config_helper_class=PNodeConfigHelper,
            chroot: str=None):
        pass


NodeDef = namedtuple('NodeDef', ['name', 'ip', 'node_port', 'client_port', 'idx',
                        'blskey', 'bls_proof', 'verkey', 'steward_nym'])

nodeParamsFileName = 'indy.env'


if __name__ == '__main__':

    
    PoolLedger.bootstrap_pool_ledger(getConfig(), nodeParamsFileName,
                                     ConfigHelper, NodeConfigHelper)