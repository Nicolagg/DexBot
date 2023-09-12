from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


#main menu
GetP = InlineKeyboardButton(text="Get price", callback_data="GetP")
Open = InlineKeyboardButton(text="🛒 Buy", callback_data="Buy")
Close = InlineKeyboardButton(text="💲 Sell", callback_data="Sell")
CloseAll = InlineKeyboardButton(text="⚙️Option", callback_data="Option")
Position = InlineKeyboardButton(text="💼 Change wallet", callback_data="change_wallet")
Addfund = InlineKeyboardButton(text="📥Add fund", callback_data="Addfund")
withdraw = InlineKeyboardButton(text="📤 withdraw", callback_data="withdraw")

mainMenu = InlineKeyboardMarkup().add(GetP).row(Open, Close).row(CloseAll).row(Position, Addfund,withdraw)


Add_token = InlineKeyboardButton(text="Add token to list ", callback_data="Add_token")
remove_token = InlineKeyboardButton(text="remove token to list ", callback_data="remove_token")





def create_buy_size_keyboard(buy_type,buysize=10, sizetype='%',slip_size=2):
    buy_sizes = [10, 20, 50, 70, 100 , None]
    buy_size_buttonP = InlineKeyboardButton(text="🔹🔹🔹Size in % 🔹🔹🔹 ", callback_data="c")
    #buy_size_buttonV = InlineKeyboardButton(text="Buy size in value", callback_data="eth")
    p10_button = InlineKeyboardButton(text="10%" if buysize != 10 else "10% ✅", callback_data="P10")
    p20_button = InlineKeyboardButton(text="20%" if buysize != 20 else "20% ✅", callback_data="P20")
    p50_button = InlineKeyboardButton(text="50%" if buysize != 50 else "50% ✅", callback_data="P50")
    p70_button = InlineKeyboardButton(text="70%" if buysize != 70 else "70% ✅", callback_data="P70")
    p100_button = InlineKeyboardButton(text="100%" if buysize != 100 else "100% ✅", callback_data="P100")
    other_button= InlineKeyboardButton(text="other :%" if buysize in buy_sizes else f'other :{buysize}% ✅', callback_data="other_size")

    silp_sizes = [2, 5, 10, 20,100, 'max' , None]

    Slip = InlineKeyboardButton(text="🔹🔹🔹Select the slippage 🔹🔹🔹", callback_data="slip")
    Slip2 = InlineKeyboardButton(text="2%" if slip_size != 2 else "2% ✅", callback_data="slip2")
    Slip5 = InlineKeyboardButton(text="5%" if slip_size != 5 else "5% ✅", callback_data="slip5")
    Slip10 = InlineKeyboardButton(text="10%" if slip_size != 10 else "10% ✅", callback_data="slip10")
    Slip20 = InlineKeyboardButton(text="20%" if slip_size != 20 else "20% ✅", callback_data="slip20")
    Slip_other = InlineKeyboardButton(text="other :%" if slip_size in silp_sizes else f'other :{slip_size}% ✅', callback_data="other_slip")
    Slip_max = InlineKeyboardButton(text="max" if slip_size != 100 else "max ✅", callback_data="slipmax")

    if buy_type == 'buy':
        buy_button = InlineKeyboardButton(text="🚀🚀🚀 Buy 🚀🚀🚀", callback_data="Execut_buy" )
    elif buy_type == 'sell':
        buy_button = InlineKeyboardButton(text="🚀🚀🚀 Sell 🚀🚀🚀", callback_data="Execut_sell" )

    canncel = InlineKeyboardButton(text="🔙", callback_data="start")



    # Create the inline keyboard
    buy_size_keyboard = InlineKeyboardMarkup().add(buy_size_buttonP).row(p10_button, p20_button, p50_button, p70_button, p100_button).row(other_button).row(Slip).row(Slip2,Slip5,Slip10,Slip20).row(Slip_other,Slip_max).row(buy_button).row(canncel)
    return buy_size_keyboard


def confirm_button(text):
    confirm_buy = InlineKeyboardButton(text=f"{text}", callback_data="confirm_buy")
    canncel_buy = InlineKeyboardButton(text="⛔ Canncel ⛔", callback_data="start")


    return InlineKeyboardMarkup().add(confirm_buy).row(canncel_buy)







def withdrawMenu(withdrawSize=10):
    withdraw_Size = [10, 20, 50, 70, 100 , None]
    buy_size_buttonP = InlineKeyboardButton(text="🔹🔹🔹how much do you want to withdraw % 🔹🔹🔹 ", callback_data="c")
    #buy_size_buttonV = InlineKeyboardButton(text="Buy size in value", callback_data="eth")
    p10_button = InlineKeyboardButton(text="10%" if withdrawSize != 10 else "10% ✅", callback_data="W10")
    p20_button = InlineKeyboardButton(text="20%" if withdrawSize != 20 else "20% ✅", callback_data="W20")
    p50_button = InlineKeyboardButton(text="50%" if withdrawSize != 50 else "50% ✅", callback_data="W50")
    p70_button = InlineKeyboardButton(text="70%" if withdrawSize != 70 else "70% ✅", callback_data="W70")
    p100_button = InlineKeyboardButton(text="100%" if withdrawSize != 100 else "100% ✅", callback_data="W100")
    other_button= InlineKeyboardButton(text="other :%" if withdrawSize in withdraw_Size else f'other :{withdrawSize}% ✅', callback_data="withdraw_other_size")
    #other_Value_button= InlineKeyboardButton(text="enter size" if withdrawSize in withdraw_Size else f'other :{withdrawSize}% ✅', callback_data="withdraw_value_size")
    view_transcaction = InlineKeyboardButton(text="Continue" , callback_data="Continue_withdraw")

    # Create the inline keyboard
    buy_size_keyboard = InlineKeyboardMarkup().add(buy_size_buttonP).row(p10_button, p20_button, p50_button, p70_button, p100_button).row(other_button).row(view_transcaction)
    return buy_size_keyboard



def continue_withdraw(text):
    confirm_buy = InlineKeyboardButton(text=f"{text}", callback_data="confirm_withdraw")
    canncel_buy = InlineKeyboardButton(text="⛔ canncel ⛔", callback_data="canncel_withdraw")


    return InlineKeyboardMarkup().add(confirm_buy).row(canncel_buy)
