from pyteal import *

def approval_program():

    # execute when Txn.applicationId() = 0
    on_creation = Seq([
        App.globalPut(Bytes("Creator"), Txn.sender()),
        App.globalPut(Bytes("tot_recycle_counter"), Int(0)),
        App.globalPut(Bytes("recyclibility_level_1"), Int(0)),
        App.globalPut(Bytes("recyclibility_level_2"), Int(0)),
        App.globalPut(Bytes("recyclibility_level_3"), Int(0)),
        App.globalPut(Bytes("recyclibility_level_4"), Int(0)),
        App.globalPut(Bytes("recyclibility_level_5"), Int(0)),
        Return(Int(1))
    ])

    # check if the sender is the creator
    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

    # get user counter
    get_value_of_user = App.localGetEx(Int(0), App.id(), Bytes("recycle_counter"))

    # get total recycle counter
    get_total_recycle = App.globalGet(Bytes("tot_recycle_counter"))

    # get recyclibility level
    get_level_1 = App.globalGet(Bytes("recyclibility_level_1"))
    get_level_2 = App.globalGet(Bytes("recyclibility_level_2"))
    get_level_3 = App.globalGet(Bytes("recyclibility_level_3"))    
    get_level_4 = App.globalGet(Bytes("recyclibility_level_4"))
    get_level_5 = App.globalGet(Bytes("recyclibility_level_5"))

    # execute on OnComplete.OptIn
    on_register = Seq([
        App.localPut(Int(0), Bytes("recycle_counter"), Int(0)),
        Return(Int(1))     
    ])

    # execute when Txn.application_args[0] = 'update_recycle_counter'
    on_increment = Seq([
        get_value_of_user,
        App.globalPut(Bytes("tot_recycle_counter"), get_total_recycle + Int(1)),
        If(Txn.application_args[0] == Bytes("1"), App.globalPut(Bytes("recyclibility_level_1"), get_level_1 + Int(1))), 
        If(Txn.application_args[0] == Bytes("2"), App.globalPut(Bytes("recyclibility_level_2"), get_level_2 + Int(1))), 
        If(Txn.application_args[0] == Bytes("3"), App.globalPut(Bytes("recyclibility_level_3"), get_level_3 + Int(1))), 
        If(Txn.application_args[0] == Bytes("4"), App.globalPut(Bytes("recyclibility_level_4"), get_level_4 + Int(1))), 
        If(Txn.application_args[0] == Bytes("5"), App.globalPut(Bytes("recyclibility_level_5"), get_level_5 + Int(1))), 
        App.localPut(Int(0), Bytes("recycle_counter"), get_value_of_user.value() + Int(1)),
        Return(Int(1))
    ])

    # execute when Txn.application_args[1] = 'check_user_counter'
    on_check = Seq([
        get_value_of_user,
        If(get_value_of_user.value() >= Int(10),
            Return(Int(1))
        ),
        Return(Int(0))
    ])

    # define approval_program
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.OptIn, on_register],
        [And(Txn.application_args[0] == Bytes("update_recycle_counter"), Txn.application_args.length() == Int(2)), on_increment],
        [Txn.application_args[0] == Bytes("check_user_counter"), on_check]    
    )

    return program

def clear_state_program():

    # get user value
    get_value_of_user = App.localGetEx(Int(0), App.id(), Bytes("recycle_counter"))

    # get total recycle value
    get_total_recycle = App.globalGet(Bytes("tot_recycle_counter"))

    # define clear_state_program
    program = Seq([
        get_value_of_user,
        App.globalPut(Bytes("tot_recycle_counter"), get_total_recycle - get_value_of_user.value()),
        App.localPut(Int(0), Bytes("recycle_counter"), Int(0)),
        Return(Int(1))
    ])

    return program

# open and compile approval_program
with open('ricicloRifiuti/approval.teal', 'w') as f:
    compiled = compileTeal(approval_program(), Mode.Application)
    f.write(compiled)

# open and compile clear_state_program
with open('ricicloRifiuti/clear_state.teal', 'w') as f:
    compiled = compileTeal(clear_state_program(), Mode.Application)
    f.write(compiled)
