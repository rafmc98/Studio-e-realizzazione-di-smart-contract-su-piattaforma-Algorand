from pyteal import *

def transportExchange():

    # conditions to check if the transaction type is Opt-in
    optIn = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.asset_amount() == Int(0),
        Txn.sender()  == Txn.asset_receiver(),
        # <ID TransportAsset>
        Txn.xfer_asset() == Int(14967831)
    )

    # conditions to check the asset exchange transactions fields and call appplication transaction fields
    controls = And(
            Gtxn[0].asset_receiver() == Gtxn[1].sender(),

            Gtxn[0].type_enum() == TxnType.AssetTransfer,
            # <ID TransportAsset>
            Gtxn[0].xfer_asset() == Int(14967831),
            Gtxn[0].asset_amount() == Int(1),
            Gtxn[0].fee() <= Int(1000),
            Gtxn[0].asset_close_to() == Global.zero_address(),
            Gtxn[0].asset_sender() == Global.zero_address(),

            Gtxn[1].type_enum() == TxnType.AssetTransfer,
            # <ID EcoAsset>
            Gtxn[1].xfer_asset() == Int(14531028),
            Gtxn[1].asset_amount() == Int(50),
            Gtxn[1].fee() <= Int(1000),
            # <Addr IsolaEcologica>
            Gtxn[1].asset_receiver() == Addr("ROV6LJIUDCSQEVX2AU7CWGOEZT2DQJUDLOYUP56MQGKVI2ECZXNUSUDOLU"),
            Gtxn[1].asset_close_to() == Global.zero_address(),
            Gtxn[1].asset_sender() == Global.zero_address(),

            # Application call to check the user value
            Gtxn[2].type_enum() == TxnType.ApplicationCall,
            Gtxn[2].sender() == Gtxn[0].asset_receiver(),
            Gtxn[2].application_id() == Int(14877441),
            Gtxn[2].application_args[0] == Bytes("check_user_value")
    )

    #  define program to check if branch to Opt-in controls or general transaction controls
    program = If(Global.group_size() == Int(3), controls, optIn)

    return program

if __name__ == "__main__":
    with open('TranEcoExchange/TranEcoExchangeContract.teal', 'w') as f:
        compiled = compileTeal(transportExchange(), Mode.Signature)
        f.write(compiled)