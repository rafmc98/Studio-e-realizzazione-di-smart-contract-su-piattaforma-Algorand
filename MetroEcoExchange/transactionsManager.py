import json
import time
import os
import base64
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk.future.transaction import AssetTransferTxn, LogicSig, LogicSigTransaction
from algosdk import encoding
from algosdk import account
from algosdk.future import transaction
from algosdk.testing import dryrun
from algosdk.v2client.models import DryrunRequest, DryrunSource

# user declared account mnemonics for account1 and account2
user_mnemonic = "laugh trade skull buyer purpose rescue enforce source hat panic reflect coach dial fiber body want south ivory viable bracket someone embody canoe above erosion"

# user declared algod connection parameters
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Initialize an algodClient
algod_client = algod.AlgodClient(algod_token, algod_address)


# Function that waits for a given txId to be confirmed by the network
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


# utility function to get address string
def get_address(mn) :
    pk_account_a = mnemonic.to_private_key(mn)
    address = account.address_from_private_key(pk_account_a)
    return address


def group_transactions():
    try:
        user = get_address(user_mnemonic)
        # read TEAL program
        data = open("MetroEcoExchange/MetroEcoExchange.teal", 'r').read()
        # compile TEAL program
        response = algod_client.compile(data)
        print("Response Result = ", response['result'])
        print("Response Hash = ", response['hash'])
    
        programstr = response['result']
        t = programstr.encode()
        # program = b"hex-encoded-program"
        program = base64.decodebytes(t)

        # create LogicSig
        lsig = LogicSig(program)

        # get user address
        user_addr = get_address(user_mnemonic)
        # convert user_mnemonic using the mnemonic.ToPrivateKey()
        user_sk = mnemonic.to_private_key(user_mnemonic)
        
        # get node suggested parameters
        params = algod_client.suggested_params()
        # comment out the next two (2) lines to use suggested fees
        params.flat_fee = True
        params.fee = 1000

        # create transactions
        # from contract account to user
        txn_0 = AssetTransferTxn(
            sender = lsig.address(), 
            sp = params, 
            receiver = user_addr,
            amt = 1, 
            index = 14638139
        )

        # from user to IsolaEcologica
        txn_1 = AssetTransferTxn(
            sender = user_addr, 
            sp = params, 
            receiver = "ROV6LJIUDCSQEVX2AU7CWGOEZT2DQJUDLOYUP56MQGKVI2ECZXNUSUDOLU", 
            amt = 15, 
            index = 14531028
        )

        
        # compute group id and put it into each transaction
        group_id = transaction.calculate_group_id([txn_0, txn_1])
        txn_0.group = group_id
        txn_1.group = group_id

        # sign transactions
        # create the LogicSigTransaction with contract account LogicSig
        stxn_0 = LogicSigTransaction(txn_0, lsig)
        stxn_1 = txn_1.sign(user_sk)
        
        # assemble transaction group
        signed_group = [stxn_0, stxn_1]
        
        # send transactions
        tx_id = algod_client.send_transactions(signed_group)

        # wait for confirmation
        wait_for_confirmation(algod_client, tx_id)

        # display confirmed transaction group
        # tx1
        confirmed_txn = algod_client.pending_transaction_info(txn_0.get_txid())
        print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

        # tx2
        confirmed_txn = algod_client.pending_transaction_info(txn_1.get_txid())
        print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

    except Exception as e:
        print(e)

group_transactions()