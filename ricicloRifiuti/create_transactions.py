import base64
import json
import datetime
from getpass import getpass
from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from algosdk.future.transaction import ApplicationNoOpTxn, AssetTransferTxn, LogicSig, LogicSigTransaction
from algosdk.account import address_from_private_key


# user wallet
user_mnemonic = "skate episode loop witness spare wish shoot symptom need veteran hurdle start fancy smooth innocent now sheriff scheme distance solution core future engage abstract same"

# creator wallet
creator_mnemonic = "sniff install spin license casino unable fly build purity soldier ability baby praise nut ripple ethics math maze palm certain illness cart jaguar ability fame"


# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])

# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key

# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

# function to calculate the recycling prize 
def calculatePrize():
    # get weigth by input
    weight = int(input("Insert weight: "))

    # get recyclability level by input
    recyclability = int(input("Insert recyclability level (range 1-5): "))

    # get the correct value based on weight
    if weight >= 0 and weight <= 10 : value = 1
    elif weight >= 11 and weight <= 50 : value = 2
    elif weight >= 51 and weight <= 100 : value = 3
    elif weight >= 101 and weight <= 200 : value = 4
    else : value = 5

    # calculate the correct asset prize amount
    return value * recyclability, weight, recyclability


# function to create and send transactions
def execute_txn(client, private_key, app_id):

    # read TEAL program
    data = open("ricicloRifiuti/ricycleStateless.teal", 'r').read()
    # compile TEAL program
    response = client.compile(data)
    print("Response Hash = ", response['hash'])

    programstr = response['result']
    t = programstr.encode()
    # program = b"hex-encoded-program"
    program = base64.decodebytes(t)
    
    # create arg to pass to TEAL program
    secCode = getpass("Insert security code: ")
    arg1 = secCode.encode()
    
    # get amount and parameters
    amount, p, r = calculatePrize()
    arg2 = (p).to_bytes(8, 'big')
    arg3 = (r).to_bytes(8,'big')

    # create LogicSig
    lsig = LogicSig(program, args = [arg1, arg2, arg3])

    # declare sender txn_1
    user = account.address_from_private_key(private_key)
   
	# get node suggested parameters
    params = client.suggested_params()
    print(params)

    # set application args txn_2
    application_args = [b'update_recycle_value', arg3]
   
    # from contract account to user
    txn_0 = AssetTransferTxn(
        sender = lsig.address(),
        revocation_target = "ROV6LJIUDCSQEVX2AU7CWGOEZT2DQJUDLOYUP56MQGKVI2ECZXNUSUDOLU",
        sp = params,
        receiver = user,
        amt = amount,
        index = 14531028
    )

    # create unsigned transaction to call app 
    txn_1 = ApplicationNoOpTxn(
        sender = user,
        sp = params, 
        index = app_id, 
        app_args = application_args
    )

    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_0, txn_1])
    txn_0.group = group_id
    txn_1.group = group_id

    # sign transactions
    # create the LogicSigTransaction with contract account LogicSig
    stxn_0 = LogicSigTransaction(txn_0, lsig)
    stxn_1 = txn_1.sign(private_key)

    # send transaction
    tx_id = client.send_transactions([stxn_0, stxn_1])

    # wait confirmation
    wait_for_confirmation(client, tx_id)

    # display confirmed transaction group
    # tx1
    confirmed_txn = client.pending_transaction_info(txn_0.get_txid())
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

    # tx2
    confirmed_txn = client.pending_transaction_info(txn_1.get_txid())
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))


def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            if formatted_key == 'voted':
                formatted_value = base64.b64decode(value['bytes']).decode('utf-8')
            else:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted


# read user local state
def read_local_state(client, addr, app_id):
    results = client.account_info(addr)
    for local_state in results['apps-local-state']:
        if local_state['id'] == app_id:
            if 'key-value' not in local_state:
                return {}
            return format_state(local_state['key-value'])
    return {}


# read app global state
def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created:
        if app['id'] == app_id:
            return format_state(app['params']['global-state'])
    return {}


def main():

    # application_id
    app_id = 14877441

    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    user_private_key = get_private_key_from_mnemonic(user_mnemonic)

    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)

    # call function to generate transactions
    execute_txn(algod_client, user_private_key, app_id)  

    print()

    # read global state of application
    print("Global state:", read_global_state(algod_client, address_from_private_key(creator_private_key), app_id))

    print()

    # read local state of application from user account
    print("Local state:", read_local_state(algod_client, address_from_private_key(user_private_key), app_id))






if __name__ == "__main__":
    main()
