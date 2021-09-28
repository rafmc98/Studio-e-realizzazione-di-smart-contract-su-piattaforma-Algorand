from pyteal import *


def algo_to_asset():

    # condition to check if transaction type is Opt-In
    optIn = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.asset_amount() == Int(0),
        Txn.sender() == Txn.asset_receiver(),
        # <ID EcoAsset>
        Txn.xfer_asset() == Int(14531028)
    )

    # conditions to check the exchange transactions fields
    controls = And(
        Gtxn[0].asset_receiver() == Gtxn[1].sender(),

        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        # <ID EcoAsset>
        Gtxn[0].xfer_asset() == Int(14531028),
        Gtxn[0].fee() <= Int(1000),
        Gtxn[0].asset_close_to() == Global.zero_address(),
        Gtxn[0].asset_sender() == Global.zero_address(),

        Gtxn[1].type_enum() == TxnType.Payment,
        Gtxn[1].amount() == Gtxn[0].asset_amount() * Int(1000000),
        Gtxn[1].fee() <= Int(1000),
        # <Addr IsolaEcologica>
        Gtxn[1].receiver() == Addr("ROV6LJIUDCSQEVX2AU7CWGOEZT2DQJUDLOYUP56MQGKVI2ECZXNUSUDOLU"),
        Gtxn[1].rekey_to() == Global.zero_address(),
        Gtxn[1].asset_close_to() == Global.zero_address(),
        Gtxn[1].close_remainder_to() == Global.zero_address(),
    )

    # define program to check if branch to Opt-in controls or general transaction controls
    program = If(Global.group_size() == Int(2), controls, optIn)

    return program


if __name__ == "__main__":
    with open('AlgoEcoExchange/AlgoEcoExchangeContract.teal', 'w') as f:
        compiled = compileTeal(algo_to_asset(), Mode.Signature)
        f.write(compiled)

