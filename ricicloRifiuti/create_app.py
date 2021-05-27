import base64
import datetime
from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod


# wallet IsolaEcologica
creator_mnemonic = "sniff install spin license casino unable fly build purity soldier ability baby praise nut ripple ethics math maze palm certain illness cart jaguar ability fame"

# user declared algod connection parameters.
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


def create_application(client, private_key, approval_program, clear_program, global_schema, local_schema):

    try:
        # define sender as creator
        sender = account.address_from_private_key(private_key)

        # declare on_complete as NoOp
        on_complete = transaction.OnComplete.NoOpOC.real

        # get node suggested parameters
        params = client.suggested_params()

        # create unsigned transaction
        txn = transaction.ApplicationCreateTxn(sender, params, on_complete, \
                                                approval_program, clear_program, \
                                                global_schema, local_schema)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        client.send_transactions([signed_txn])

        # await confirmation
        wait_for_confirmation(client, tx_id)

        # display results
        transaction_response = client.pending_transaction_info(tx_id)
        app_id = transaction_response['application-index']
        print("Created new app-id:", app_id)
    
    except Exception as e:
        print(e)

def main():

    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)

    # declare application state storage
    local_ints = 1      # to store the user recycle value
    local_bytes = 0
    global_ints = 6     # to store the total recycle value
    global_bytes = 1    # to store the creator address

    # set application state storage
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

     # get Teal approval program
    approval_program_teal = open("ricicloRifiuti/approval.teal", 'r').read()
    # compile program to binary
    approval_program_compiled = compile_program(algod_client, approval_program_teal)

    # get PyTeal clear state program
    clear_state_program_teal = open("ricicloRifiuti/clear_state.teal", 'r').read()
    # compile program to binary
    clear_state_program_compiled = compile_program(algod_client, clear_state_program_teal)

    # create new application
    app_id = create_application(algod_client, creator_private_key, approval_program_compiled, clear_state_program_compiled, global_schema, local_schema)

if __name__ == "__main__":
    main()