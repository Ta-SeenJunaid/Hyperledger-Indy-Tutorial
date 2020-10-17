import time

from indy import  did, ledger, pool, wallet

import json
import logging

import argparse
import sys
from ctypes import *
from indy.error import ErrorCode, IndyError

from src.utils import get_pool_genesis_txn_path, run_coroutine, PROTOCOL_VERSION


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Run python sdk_sample scenario')
parser.add_argument('-t', '--storage_type', help='load custom wallet storage plug-in')
parser.add_argument('-l', '--library', help='dynamic library to load for plug-in')
parser.add_argument('-e', '--entrypoint', help='entry point for dynamic library')
parser.add_argument('-c', '--config', help='entry point for dynamic library')
parser.add_argument('-s', '--creds', help='entry point for dynamic library')

args = parser.parse_args()

if args.storage_type:
    if not (args.library and args.entrypoint):
        parser.print_help()
        sys.exit(0)
    stg_lib = CDLL(args.library)
    result = stg_lib[args.entrypoint]()
    if result != 0:
        print("Error unable to load wallet storage", result)
        parser.print_help()
        sys.exit(0)

    if args.storage_type == "postgres_storage":
        try:
            print("Calling init_storagetype() for postgres:", args.config, args.creds)
            init_storagetype = stg_lib["init_storagetype"]
            c_config = c_char_p(args.config.encode('utf-8'))
            c_credentials = c_char_p(args.creds.encode('utf-8'))
            result = init_storagetype(c_config, c_credentials)
            print(" ... returns ", result)
        except RuntimeError as e:
            print("Error initializing storage, ignoring ...", e)

    print("Success, loaded wallet storage", args.storage_type)


async def run():
    logger.info("SDK application started ----------> started")

    pool_ = {
        'name': 'my_pool'
    }
    logger.info("Open Pool Ledger: {}".format(pool_['name']))
    pool_['genesis_txn_path'] = get_pool_genesis_txn_path(pool_['name'])
    pool_['config'] = json.dumps({"genesis_txn": str(pool_['genesis_txn_path'])})

    
    await pool.set_protocol_version(PROTOCOL_VERSION)

    try:
        await pool.create_pool_ledger_config(pool_['name'], pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

    logger.info("==============================")
    logger.info("=== Getting Trust Anchor credentials for College, Company, Bank and Government  ==")
    logger.info("------------------------------")

    steward = {
        'name': "Steward1",
        'wallet_config': json.dumps({'id': 'steward1_wallet'}),
        'wallet_credentials': json.dumps({'key': 'steward1_wallet_key'}),
        'pool': pool_['handle'],
        'seed': '100A000000300000c0000000Steward1'
    }

    await create_wallet(steward)

    logger.info("\"Steward1\" -> Create and store in Wallet DID from seed")
    steward['did_info'] = json.dumps({'seed': steward['seed']})
    steward['did'], steward['key'] = await did.create_and_store_my_did(steward['wallet'], steward['did_info'])

    logger.info("==============================")
    logger.info("== Steward did and key  ==")
    print("seed")
    print(steward['seed'])
    print("did")
    print(steward['did'])
    print("key")
    print(steward['key'])
    logger.info("------------------------------")

    logger.info("==============================")
    logger.info("== Getting Trust Anchor credentials - Government getting Verinym  ==")
    logger.info("------------------------------")

    government = {
        'name': 'Government',
        'wallet_config': json.dumps({'id': 'government_wallet'}),
        'wallet_credentials': json.dumps({'key': 'government_wallet_key'}),
        'pool': pool_['handle'],
        'role': 'TRUST_ANCHOR'
    }

    await getting_verinym(steward, government)

    logger.info("==============================")
    logger.info("== Getting Trust Anchor credentials - College getting Verinym  ==")
    logger.info("------------------------------")

    college = {
        'name': 'College',
        'wallet_config': json.dumps({'id': 'college_wallet'}),
        'wallet_credentials': json.dumps({'key': 'college_wallet_key'}),
        'pool': pool_['handle'],
        'role': 'TRUST_ANCHOR'
    }

    await getting_verinym(steward, college)

    logger.info("==============================")
    logger.info("== Getting Trust Anchor credentials - Company getting Verinym  ==")
    logger.info("------------------------------")

    company = {
        'name': 'Company',
        'wallet_config': json.dumps({'id': 'company_wallet'}),
        'wallet_credentials': json.dumps({'key': 'company_wallet_key'}),
        'pool': pool_['handle'],
        'role': 'TRUST_ANCHOR'
    }

    await getting_verinym(steward, company)

    logger.info("==============================")
    logger.info("== Getting Trust Anchor credentials - Bank getting Verinym  ==")
    logger.info("------------------------------")

    bank = {
        'name': 'Bank',
        'wallet_config': json.dumps({'id': 'bank_wallet'}),
        'wallet_credentials': json.dumps({'key': 'bank_wallet_key'}),
        'pool': pool_['handle'],
        'role': 'TRUST_ANCHOR'
    }

    await getting_verinym(steward, bank)






    logger.info("==============================")

    logger.info(" \"Steward1\" -> Close and Delete wallet")
    await wallet.close_wallet(steward['wallet'])
    await wallet.delete_wallet(steward['wallet_config'], steward['wallet_credentials'])

    logger.info("\"Government\" -> Close and Delete wallet")
    await wallet.close_wallet(government['wallet'])
    await wallet.delete_wallet(wallet_config("delete", government['wallet_config']),
                               wallet_credentials("delete", government['wallet_credentials']))

    logger.info("\"College\" -> Close and Delete wallet")
    await wallet.close_wallet(college['wallet'])
    await wallet.delete_wallet(wallet_config("delete", college['wallet_config']),
                               wallet_credentials("delete", college['wallet_credentials']))

    logger.info("\"Company\" -> Close and Delete wallet")
    await wallet.close_wallet(company['wallet'])
    await wallet.delete_wallet(wallet_config("delete", company['wallet_config']),
                               wallet_credentials("delete", company['wallet_credentials']))

    logger.info("\"Bank\" -> Close and Delete wallet")
    await wallet.close_wallet(bank['wallet'])
    await wallet.delete_wallet(wallet_config("delete", bank['wallet_config']),
                               wallet_credentials("delete", bank['wallet_credentials']))

    logger.info("Close and Delete pool")
    await pool.close_pool_ledger(pool_['handle'])
    await pool.delete_pool_ledger_config(pool_['name'])

    logger.info("Getting started -> done")



def wallet_config(operation, wallet_config_str):
    if not args.storage_type:
        return wallet_config_str
    wallet_config_json = json.loads(wallet_config_str)
    wallet_config_json['storage_type'] = args.storage_type
    if args.config:
        wallet_config_json['storage_config'] = json.loads(args.config)

    return json.dumps(wallet_config_json)


def wallet_credentials(operation, wallet_credentials_str):
    if not args.storage_type:
        return wallet_credentials_str
    wallet_credentials_json = json.loads(wallet_credentials_str)
    if args.creds:
        wallet_credentials_json['storage_credentials'] = json.loads(args.creds)

    return json.dumps(wallet_credentials_json)



async def create_wallet(identity):
    logger.info("\"{}\" -> Create wallet".format(identity['name']))
    try:
        await wallet.create_wallet(wallet_config("create", identity['wallet_config']),
                                   wallet_credentials("create", identity['wallet_credentials']))
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    identity['wallet'] = await wallet.open_wallet(wallet_config("open", identity['wallet_config']),
                                                  wallet_credentials("open", identity['wallet_credentials']))


async def getting_verinym(from_, to):
    await create_wallet(to)

    (to['did'], to['key']) = await did.create_and_store_my_did(to['wallet'], "{}")

    from_['info'] = {
        'did': to['did'],
        'verkey': to['key'],
        'role': to['role'] or None
    }

    await send_nym(from_['pool'], from_['wallet'], from_['did'], from_['info']['did'],
                   from_['info']['verkey'], from_['info']['role'])

async def send_nym(pool_handle, wallet_handle, _did, new_did, new_key, role):
    nym_request = await ledger.build_nym_request(_did, new_did, new_key, None, role)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, nym_request)



if __name__ == '__main__':
    run_coroutine(run)
    time.sleep(1)