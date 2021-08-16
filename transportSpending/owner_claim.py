import json
import base64
import time
from hashlib import sha256
from getpass import getpass
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk.future.transaction import  AssetTransferTxn, LogicSig, LogicSigTransaction
from algosdk.v2client.models import DryrunRequest, DryrunSource


algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Initialize an algod client
algod_client = algod.AlgodClient(algod_token=algod_token, algod_address=algod_address)

# declare user address
user_addr = "T5HO4K4RAPASDATFJRTPW66ADGOGSR6DPTPI6PGH54KVV76NYCH7LB4NUE"

# Function that waits for a given txId to be confirmed by the network
def wait_for_confirmation(txid, start_time):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = algod_client.status().get('last-round')
    txinfo = algod_client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        algod_client.status_after_block(last_round)
        txinfo = algod_client.pending_transaction_info(txid)
    print("Tempo accettazione transazione:", time.time() - start_time)
    #print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo


# function to create the owner claim transaction
def owner_claim():
    # read TEAL program
    data = open("transportSpending/escrow.teal", 'r').read()
    # compile TEAL program
    response = algod_client.compile(data)
    print("Response Result = ", response['result'])
    print("Response Hash = ", response['hash'])
 
    # set the program string
    programstr = response['result']
    t = programstr.encode()
    # program = b"hex-encoded-program"
    program = base64.decodebytes(t)

    arg = "ctr".encode()
     
    # create LogicSig
    lsig = LogicSig(program, args = [arg])
   
    # define sender
    snd = lsig.address()

    # transfer ecoAsset to user account
    params = algod_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True
    
    # transaction from contract account to owner
    txn = AssetTransferTxn(
        sender = snd,
        sp = params,
        receiver = user_addr,
        amt = 1,
        index = 14967831
    )

    # create the LogicSigTransaction with contract account LogicSig
    lstx = LogicSigTransaction(txn, lsig)

    # send raw LogicSigTransaction to network
    txid = algod_client.send_transaction(lstx)
    #print("Transaction ID: " + txid)
    
    # wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(txid, time.time())
    
    print()
    
    #print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

owner_claim()

