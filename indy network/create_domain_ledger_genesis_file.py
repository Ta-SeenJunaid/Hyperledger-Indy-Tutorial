import argparse
import fileinput
import os

from ledger.genesis_txn.genesis_txn_file_util import create_genesis_txn_init_ledger


from indy_common.config_helper import ConfigHelper
from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields

from plenum.common.member.member import Member


from plenum.common.config_helper import PConfigHelper
from plenum.common.constants import TRUSTEE, STEWARD
from stp_core.common.util import adict


class DomainLedger:

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

    
    @staticmethod
    def _bootstrap_args_type_verkeys(verkeys_str_arg):
        verkeys = []
        i =1 
        for arg in verkeys_str_arg.split(','):
            arg = str(arg)
            arg = arg.strip()
            if len(arg) != 23:
                raise argparse.ArgumentTypeError("The lenght verification key {} should be 23 digit long".format(i))           
            verkeys.append(arg)
            i += 1

        return verkeys


    @classmethod 
    def gen_def(cls, dids, verkeys):

        defs = []
        for i in range(1, len(dids)+1):
            d = adict()
            d.nym = dids[i-1]
            d.verkey = verkeys[i-1]
            defs.append(d)

        return defs

    @classmethod
    def init_domain_ledger(cls, appendToLedgers, genesis_dir, config, domainTxnFieldOrder):
        domain_txn_file = cls.domain_ledger_file_name(config)
        domain_ledger = create_genesis_txn_init_ledger(genesis_dir, domain_txn_file)
        if not appendToLedgers:
            domain_ledger.reset()
        return domain_ledger

    @classmethod
    def domain_ledger_file_name(cls, config):
        return config.domainTransactionsFile

    @classmethod
    def bootstrap_domain_ledger(cls, config=getConfig(), config_helper_class=PConfigHelper,
                                domainTxnFieldOrder=getTxnOrderedFields(), chroot: str=None):
        parser = argparse.ArgumentParser(description="Generate domain transactions")
        parser.add_argument('--trusteeDids', required=True,
                            help='Trustee Dids, provide comma separated dids',
                            type=cls._bootstrap_args_type_dids)
        parser.add_argument('--trusteeVerkeys', required=True,
                            help='Trustees Verkey, provide comma separated verification keys',
                            type=cls. _bootstrap_args_type_verkeys)
        parser.add_argument('--stewardDids', required=True,
                            help='Stewards Dids, provide comma separated dids',
                            type=cls._bootstrap_args_type_dids)
        parser.add_argument('--stewardVerkeys', required=True,
                            help='Stewards Verkey, provide comma separated verification keys',
                            type=cls. _bootstrap_args_type_verkeys)
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

        if (len(args.trusteeDids) != len(args.trusteeVerkeys)):
            raise argparse.ArgumentTypeError("Every Trustee did must need to have  it's "
                                             "corresponding verification key and vice versa")

        if (len(args.stewardDids) != len(args.stewardVerkeys)):
            raise argparse.ArgumentTypeError("Every Steward did must need to have it's "
                                             "corresponding verification key and vice versa")


        for line in fileinput.input(['/etc/indy/indy_config.py'], inplace=True):
            if 'NETWORK_NAME' not in line:
                print(line, end="")
        with open('/etc/indy/indy_config.py', 'a') as cfgfile:
            cfgfile.write("NETWORK_NAME = '{}'".format(args.network))


        trustee_defs = cls.gen_def(args.trusteeDids, args.trusteeVerkeys)
        steward_defs = cls.gen_def(args.stewardDids, args.stewardVerkeys)


        cls.bootstrap_domain_ledger_core(config, args.network, args.appendToLedgers, domainTxnFieldOrder,
                             trustee_defs, steward_defs, config_helper_class)



    @classmethod 
    def bootstrap_domain_ledger_core(
            cls,
            config,
            network,
            appendToLedgers,
            domainTxnFieldOrder,
            trustee_defs,
            steward_defs,
            config_helper_class=PConfigHelper,
            chroot: str=None):

       
        config.NETWORK_NAME = network

        config_helper = config_helper_class(config, chroot=chroot)
        os.makedirs(config_helper.genesis_dir, exist_ok=True)
        genesis_dir = config_helper.genesis_dir


        domainLedger = cls.init_domain_ledger(appendToLedgers, genesis_dir,
                                              config, domainTxnFieldOrder)

        genesis_protocol_version = None

        seq_no = 1

        for td in trustee_defs:
            trustee_txn = Member.nym_txn(td.nym, verkey=td.verkey,
                                        role=TRUSTEE, seq_no=seq_no,
                                        protocol_version=genesis_protocol_version)
            
            seq_no += 1
            domainLedger.add(trustee_txn)

        for sd in steward_defs:
            nym_txn = Member.nym_txn(sd.nym, verkey=sd.verkey, role=STEWARD, 
                                    creator= trustee_defs[0].nym, seq_no=seq_no,
                                    protocol_version=genesis_protocol_version)
            seq_no += 1
            domainLedger.add(nym_txn)


        domainLedger.stop()

        


if __name__ == '__main__':

    
    DomainLedger.bootstrap_domain_ledger(getConfig(), ConfigHelper, getTxnOrderedFields())