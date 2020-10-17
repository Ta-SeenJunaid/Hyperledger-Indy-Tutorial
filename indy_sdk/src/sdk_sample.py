import time

from indy import  anoncreds, did, ledger, pool, wallet, blob_storage

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
    logger.info("=== Credential Schemas Setup ==")
    logger.info("------------------------------")

    logger.info("\"Government\" -> Create \"Job-Certificate\" Schema")
    job_certificate = {
        'name': 'Job-Certificate',
        'version': '0.2',
        'attributes': ['first_name', 'last_name', 'salary', 'employee_status', 'experience']
    }
    (government['job_certificate_schema_id'], government['job_certificate_schema']) = \
        await anoncreds.issuer_create_schema(government['did'], job_certificate['name'], job_certificate['version'],
                                             json.dumps(job_certificate['attributes']))
    job_certificate_schema_id = government['job_certificate_schema_id']

    logger.info("\"Government\" -> Send \"Job-Certificate\" Schema to Ledger")
    await send_schema(government['pool'], government['wallet'], government['did'], government['job_certificate_schema'])

    logger.info("\"Government\" -> Create \"Transcript\" Schema")
    transcript = {
        'name': 'Transcript',
        'version': '1.2',
        'attributes': ['first_name', 'last_name', 'degree', 'status', 'year', 'average', 'ssn']
    }
    (government['transcript_schema_id'], government['transcript_schema']) = \
        await anoncreds.issuer_create_schema(government['did'], transcript['name'], transcript['version'],
                                             json.dumps(transcript['attributes']))
    transcript_schema_id = government['transcript_schema_id']

    logger.info("\"Government\" -> Send \"Transcript\" Schema to Ledger")
    await send_schema(government['pool'], government['wallet'], government['did'], government['transcript_schema'])

    time.sleep(1)  


    logger.info("==============================")
    logger.info("=== College Credential Definition Setup ==")
    logger.info("------------------------------")

    logger.info("\"College\" -> Get \"Transcript\" Schema from Ledger")
    (college['transcript_schema_id'], college['transcript_schema']) = \
        await get_schema(college['pool'], college['did'], transcript_schema_id)

    logger.info("\"College\" -> Create and store in Wallet \"College Transcript\" Credential Definition")
    transcript_cred_def = {
        'tag': 'TAG1',
        'type': 'CL',
        'config': {"support_revocation": False}
    }
    (college['transcript_cred_def_id'], college['transcript_cred_def']) = \
        await anoncreds.issuer_create_and_store_credential_def(college['wallet'], college['did'],
                                                               college['transcript_schema'], transcript_cred_def['tag'],
                                                               transcript_cred_def['type'],
                                                               json.dumps(transcript_cred_def['config']))

    logger.info("\"College\" -> Send  \"College Transcript\" Credential Definition to Ledger")
    await send_cred_def(college['pool'], college['wallet'], college['did'], college['transcript_cred_def'])


    logger.info("==============================")
    logger.info("=== Company Credential Definition Setup ==")
    logger.info("------------------------------")

    logger.info("\"Company\" -> Get from Ledger \"Job-Certificate\" Schema")
    (company['job_certificate_schema_id'], company['job_certificate_schema']) = \
        await get_schema(company['pool'], company['did'], job_certificate_schema_id)

    logger.info("\"Company\" -> Create and store in Wallet \"Company Job-Certificate\" Credential Definition")
    job_certificate_cred_def = {
        'tag': 'TAG1',
        'type': 'CL',
        'config': {"support_revocation": True}
    }
    (company['job_certificate_cred_def_id'], company['job_certificate_cred_def']) = \
        await anoncreds.issuer_create_and_store_credential_def(company['wallet'], company['did'],
                                                               company['job_certificate_schema'],
                                                               job_certificate_cred_def['tag'],
                                                               job_certificate_cred_def['type'],
                                                               json.dumps(job_certificate_cred_def['config']))

    logger.info("\"Company\" -> Send \"Company Job-Certificate\" Credential Definition to Ledger")
    await send_cred_def(company['pool'], company['wallet'], company['did'], company['job_certificate_cred_def'])

    logger.info("\"Company\" -> Creates Revocation Registry")
    company['tails_writer_config'] = json.dumps({'base_dir': "/tmp/indy_company_tails", 'uri_pattern': ''})
    tails_writer = await blob_storage.open_writer('default', company['tails_writer_config'])
    (company['revoc_reg_id'], company['revoc_reg_def'], company['revoc_reg_entry']) = \
        await anoncreds.issuer_create_and_store_revoc_reg(company['wallet'], company['did'], 'CL_ACCUM', 'TAG1',
                                                          company['job_certificate_cred_def_id'],
                                                          json.dumps({'max_cred_num': 5,
                                                                      'issuance_type': 'ISSUANCE_ON_DEMAND'}),
                                                          tails_writer)

    logger.info("\"Company\" -> Post Revocation Registry Definition to Ledger")
    company['revoc_reg_def_request'] = await ledger.build_revoc_reg_def_request(company['did'], company['revoc_reg_def'])
    await ledger.sign_and_submit_request(company['pool'], company['wallet'], company['did'], company['revoc_reg_def_request'])

    logger.info("\"Company\" -> Post Revocation Registry Entry to Ledger")
    company['revoc_reg_entry_request'] = \
        await ledger.build_revoc_reg_entry_request(company['did'], company['revoc_reg_id'], 'CL_ACCUM',
                                                   company['revoc_reg_entry'])
    await ledger.sign_and_submit_request(company['pool'], company['wallet'], company['did'], company['revoc_reg_entry_request'])





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

async def send_schema(pool_handle, wallet_handle, _did, schema):
    schema_request = await ledger.build_schema_request(_did, schema)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, schema_request)

async def send_cred_def(pool_handle, wallet_handle, _did, cred_def_json):
    cred_def_request = await ledger.build_cred_def_request(_did, cred_def_json)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, cred_def_request)

async def get_schema(pool_handle, _did, schema_id):
    get_schema_request = await ledger.build_get_schema_request(_did, schema_id)
    get_schema_response = await ensure_previous_request_applied(
        pool_handle, get_schema_request, lambda response: response['result']['data'] is not None)
    return await ledger.parse_get_schema_response(get_schema_response)



if __name__ == '__main__':
    run_coroutine(run)
    time.sleep(1)