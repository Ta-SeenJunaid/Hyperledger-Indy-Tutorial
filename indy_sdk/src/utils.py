import asyncio
import json
from os import environ
from pathlib import Path
from tempfile import gettempdir

import time
from indy import ledger


PROTOCOL_VERSION = 2


def path_home() -> Path:
    return Path.home().joinpath(".indy_client")


def get_pool_genesis_txn_path(pool_name):
    path_temp = Path(gettempdir()).joinpath("indy")
    path = path_temp.joinpath("{}.txn".format(pool_name))
    save_pool_genesis_txn_file(path)
    return path


def pool_genesis_txn_data():

    return "\n".join(['{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node1","blskey":"tP6NHFxgWayNLXWrAu6jSdkauHRAmViF11BhELfNenMJxC9vbg7GQwqh1W9w3bzbR6kCSjZuqwfktvtdzzx8Bx1NZuWzUN9a7nEehRWjH4ozKPH7P6tw6Et9W1yyX7wj33nVWAotZ2r9zoYouGV7ybg9ijmQHhYiqAYqXerQ6n7zD2","blskey_pop":"QwxHLEJFt1HXuE7P6UdpXztNaNVAoFdiTbhMGXtQgPFCC7GbSG5UAXPFHdkmfsSV9jjyVataX2ujKCEqZn2hpxcnfeBEYioYdqehPGH2VLh1Qw3XZKC3vFW1kc3uMaRtHqWWR6m4Enu2qLuSdFcLtYCJreDpHghB8ds42QHXwoZ8T1","client_ip":"127.0.0.1","client_port":9702,"node_ip":"127.0.0.1","node_port":9701,"services":["VALIDATOR"]},"dest":"A1vayc9P6mX7HumjQgFsJEcAzNPkPUTfadUfVREEcBuG"},"metadata":{"from":"RnXJMDxifkBaceAkPizz8F"},"type":"0"},"txnMetadata":{"seqNo":1,"txnId":"fea82e10e894419fe2bea7d96296a6d46f50f93f9eeda954ec461b2ed2950b62"},"ver":"1"}','{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node2","blskey":"CkXUu3Sqrm8212ahXf2G6fpQctMW86rPR5o4AFi5LJytw3NsDPzba83m5xCNuvSS353NYEdDg8EZtsWEDMMpgUpAJAB1hYzaxAybcozwkYgoSi941wi6HqJHiNLxWgHzizwXGRY2KymcTqC385WkGnMLew6SzhajcP8wVniyZRz3pi","blskey_pop":"QmrjxheeyDAFknchT4AEBLD6fKVLS9ZMuXDmhstXXnecB64zBtzgmUFHQgoHtrvfPU6A4RS1uWb3AjBVBZh8QBquB1DMfGTGpYszvCQDhgLJtnvrJjVX7whtVT4r33KyCvicPyHXk1ku3H3MYJSbKgC8a9NUv19q2BugsZn1nLSgHm","client_ip":"127.0.0.1","client_port":9704,"node_ip":"127.0.0.1","node_port":9703,"services":["VALIDATOR"]},"dest":"5xKjnTcyK33VcZ5ZSSaX3rD2KXcEX2etdYr1PHjXopvZ"},"metadata":{"from":"AmJHyEZ9ofrPz1DUfx97Qo"},"type":"0"},"txnMetadata":{"seqNo":2,"txnId":"1ac8aece2a18ced660fef8694b61aac3af08ba875ce3026a160acbc3a3af35fc"},"ver":"1"}','{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node3","blskey":"ftbhBQme51s3UZPavohqouyQkGNWf43fDn9ddey1Jm1vGpoquWh3suR9MCEj4BVvfnwnd7BiLGwSb6FfHF3wwPxYqKdzi3qq4MrxRkTDFCm7ZmbTPBkuSUy5Yr41cFeGFDP21TrZrYZb8oNjYCbJe9VxskrJyXpmbY2s2hWWVCsTNe","blskey_pop":"Qy4DvpUTGiegNyaNhhPXv2oURCciHASsWV9YPB44wsopipJd8Yknu6pJ2Nm4m6BoFGmAnRMHNhw6LupYyNY1UGQkwrSZkFWERExrKMYS7xyi33K1PDpzoM3Wfag7ivLCBHRqfsUpbSBep3VgyqogEGCwmwSkVVSe7kJDBsNW9JYVnw","client_ip":"127.0.0.1","client_port":9706,"node_ip":"127.0.0.1","node_port":9705,"services":["VALIDATOR"]},"dest":"5SQvs8Ywtxwei3k3FVmMaxmb6ccNdpZ6payDynWQ2igN"},"metadata":{"from":"PeVR5pdFizbK8WN9THd3mq"},"type":"0"},"txnMetadata":{"seqNo":3,"txnId":"7e9f355dffa78ed24668f0e0e369fd8c224076571c51e2ea8be5f26479edebe4"},"ver":"1"}'])


def save_pool_genesis_txn_file(path):
    data = pool_genesis_txn_data()

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(str(path), "w+") as f:
        f.writelines(data)


def run_coroutine(coroutine, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    loop.run_until_complete(coroutine())


async def ensure_previous_request_applied(pool_handle, checker_request, checker):
    for _ in range(3):
        response = json.loads(await ledger.submit_request(pool_handle, checker_request))
        try:
            if checker(response):
                return json.dumps(response)
        except TypeError:
            pass
        time.sleep(5)
