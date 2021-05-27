from pyteal import *

# user address
owner = Addr("T5HO4K4RAPASDATFJRTPW66ADGOGSR6DPTPI6PGH54KVV76NYCH7LB4NUE")

# AddettoTrasporti address
rcv = Addr("I3WYMLEMCAGJHLXNYCNH723WKGTITPKLXFOMEXSWQP5XOHYYYXBPAHJ56Q")

# secret word to receiver closeOut 
secret = Bytes("base32", "2323232323232323")

# timeout time to owner closeOut
timeout = "<Round Timeout>"

def htlc(tmpl_owner = owner,
             tmpl_receiver = rcv,
             tmpl_secret = secret,
             tmpl_hash_fn = Sha256,
             tmpl_timeout = timeout):

    # conditions to check if the transaction type is Opt-in
    optIn = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.asset_amount() == Int(0),
        Txn.sender()  == Txn.asset_receiver(),
        # <ID TransportAsset>
        Txn.xfer_asset() == Int(14967831)
    )

    # general safety conditions
    safety_cond = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.xfer_asset() == Int(14967831),
        Txn.fee() <= Int(1000),
        Txn.asset_close_to() == Global.zero_address(),
        Txn.asset_sender() == Global.zero_address(),
    )

    # receiver conditions to closeOut 
    receiver_cond = And(
        Txn.receiver() == tmpl_receiver,
        tmpl_hash_fn(Arg(0)) == tmpl_secret
    )

    # owner conditions to closeOut
    owner_cond = And(
        Txn.receiver() == tmpl_owner,
        Txn.first_valid() > Int(tmpl_timeout)
    )

    # define the program
    return Or(
        optIn,
        And(safety_cond,Or(receiver_cond, owner_cond))
    )


if __name__ == "__main__":
    with open('transportSpending/spending.teal', 'w') as f:
        compiled = compileTeal(htlc(), Mode.Signature)
        f.write(compiled)

