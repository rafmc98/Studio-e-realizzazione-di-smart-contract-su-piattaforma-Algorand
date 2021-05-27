from pyteal import *

def assetExchange():

    # conditions to check if the transaction type is Opt-in
    optIn = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.asset_amount() == Int(0),
        Txn.sender()  == Txn.asset_receiver(),
        # <ID MetroAsset>
        Txn.xfer_asset() == Int(14638139)
    )

    # conditions to check the asset exchange transactions fields 
    controls = And(
        Gtxn[0].asset_receiver() == Gtxn[1].sender(),

        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        # <ID MetroAsset>
        Gtxn[0].xfer_asset() == Int(14638139),
        Gtxn[0].asset_amount() == Int(1),
        Gtxn[0].fee() <= Int(1000),
        Gtxn[0].asset_close_to() == Global.zero_address(),
        Gtxn[0].asset_sender() == Global.zero_address(),

        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        # <ID EcoAsset>
        Gtxn[1].xfer_asset() == Int(14531028),
        Gtxn[1].asset_amount() == Int(15),
        Gtxn[1].fee() <= Int(1000),
        Gtxn[1].asset_close_to() == Global.zero_address(),
        # <Addr IsolaEcologica>
        Gtxn[1].asset_receiver() == Addr("ROV6LJIUDCSQEVX2AU7CWGOEZT2DQJUDLOYUP56MQGKVI2ECZXNUSUDOLU"),
        Gtxn[1].asset_sender() == Global.zero_address(),
    )

    # define program to check if branch to Opt-in controls or general transaction controls
    program = If(Global.group_size() == Int(2), controls, optIn)

    return program


if __name__ == "__main__":
    with open('assetExchange/assetExchange.teal', 'w') as f:
        compiled = compileTeal(assetExchange(), Mode.Signature)
        f.write(compiled)


    