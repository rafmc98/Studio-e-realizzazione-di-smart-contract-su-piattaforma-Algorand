import base64
from pyteal import *

asset_id = Int(14531028)
secret_code = [ Bytes("base64", str(base64.b64encode('1799912'.encode()), 'utf-8')),
                Bytes("base64", str(base64.b64encode('abcd'.encode()), 'utf-8')),
                Bytes("base64", str(base64.b64encode('1234'.encode()), 'utf-8')),
                Bytes("base64", str(base64.b64encode('0000'.encode()), 'utf-8'))
              ]
max_fee = Int(1000)
asnd = Addr("ROV6LJIUDCSQEVX2AU7CWGOEZT2DQJUDLOYUP56MQGKVI2ECZXNUSUDOLU")


def premioRiciclo( asset_id = asset_id, 
                   max_fee = max_fee,
                   secret_code = secret_code,
                   asnd = asnd):

    # conditions to check if the assetAmount is correct
    amount_controls = Or(
        And(Btoi(Arg(1)) >= Int(0), Btoi(Arg(1)) <= Int(10), Gtxn[0].asset_amount() == Int(1) * Btoi(Arg(2))),
        And(Btoi(Arg(1)) >= Int(11), Btoi(Arg(1)) <= Int(50), Gtxn[0].asset_amount() == Int(2) * Btoi(Arg(2))),
        And(Btoi(Arg(1)) >= Int(51), Btoi(Arg(1)) <= Int(100), Gtxn[0].asset_amount() == Int(3) * Btoi(Arg(2))),
        And(Btoi(Arg(1)) >= Int(101), Btoi(Arg(1)) <= Int(200), Gtxn[0].asset_amount() == Int(4) * Btoi(Arg(2))),
        And(Btoi(Arg(1)) >= Int(201), Gtxn[0].asset_amount() == Int(5) * Btoi(Arg(2)))
    )

    # conditions to check if the security code is correct
    sec_control = Or(
        Arg(0) == secret_code[0],
        Arg(0) == secret_code[1],
        Arg(0) == secret_code[2],
        Arg(0) == secret_code[3]
    )

    # conditions to check transactions fields
    controls = And(

        # transaction from account to user
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].xfer_asset() == asset_id,
        Gtxn[0].asset_amount() <= Int(25),
        Gtxn[0].asset_sender() == asnd,
        Gtxn[0].rekey_to() == Global.zero_address(),
        Gtxn[0].asset_close_to() == Global.zero_address(),
        Gtxn[0].close_remainder_to() == Global.zero_address(),
        Gtxn[0].fee() <= max_fee,

        # transaction to call app
        Gtxn[1].type_enum() == TxnType.ApplicationCall,
        Gtxn[1].sender() == Gtxn[0].asset_receiver(),
        Gtxn[1].application_id() == Int(14877441),
        Gtxn[1].application_args[0] == Bytes("update_recycle_value"),
    )
    
    return And(amount_controls, controls, sec_control)

if __name__ == "__main__":
    with open('EcoRecycle/EcoRecycleContract.teal', 'w') as f:
        compiled = compileTeal(premioRiciclo(), Mode.Signature)
        f.write(compiled)