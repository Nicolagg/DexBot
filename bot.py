from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import Session
from models import User
from blockchain import *
from button import * 
from helpers import *


# Initialiser le Dictionnaire des Ordres
orders_data = {}

withdraw_data = {}

#import connection yaml file c
with open('connection.yaml', 'r') as f: 
    connection = yaml.safe_load(f)

API_TOKEN= connection['telegram']['API_TOKEN']


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



# States for buy orther
class Form(StatesGroup):
    buy_size = State()  
    sipp_size = State()  
    contract = State()  


# States to change wallet
class walletForm(StatesGroup):
    wallet = State()  


# States withdraw
class withdrawForm(StatesGroup):
    address = State()  
    withdraw_size = State()  



@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    session = Session()
    chat_id = message.chat.id

    user = session.query(User).filter_by(chat_id=chat_id).first()
    if not user:
        
        private_key, address =generate_address()

        user = User(chat_id=chat_id, address=address,private_key=private_key )
        session.add(user)
        session.commit()

        answer_string = f"""
Hello new user
your new wallet
Private key:
{private_key}
Address:
{address}
"""     
    
        await  message.answer(answer_string, reply_markup=mainMenu)
    else:
        ETH_balance = get_ETH_balance(chat_id)
        answer_string = f"Welcome back!\nI'm your crypto bot.\nYour ETH balance is {ETH_balance} "
        await  message.answer(answer_string, reply_markup=mainMenu) 
    session.close()

dp.callback_query_handler(text=["start"])
async def start(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    ETH_balance = get_ETH_balance(chat_id)
    answer_string = f"Welcome back! I'm your crypto bot.\nYour ETH balance is {ETH_balance} "
    await  bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=call.message.message_id,
                                            reply_markup=mainMenu)


@dp.callback_query_handler(text=["GetP", "Buy", "Sell", "Addfund", "withdraw"])
async def start_menu(call: types.CallbackQuery, state: FSMContext):
    global bot
    chat_id = call.message.chat.id
    
    
    if call.data == "Buy":
        orders_data[chat_id] = {'type' : 'buy',
                                'amount':1,
                                'slippage':2}

        aaa = create_buy_size_keyboard('buy')
        await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=call.message.message_id,
                                            reply_markup=aaa)
        # edit_message_reply_markup
        # await call.message.answer(text,reply_markup=BuySize)


    if call.data == "Sell":
        orders_data[chat_id] = {'type' : 'sell',
                                'amount':1,
                                'slippage':2}

        aaa = create_buy_size_keyboard('sell')
        await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=call.message.message_id,
                                            reply_markup=aaa)
    if call.data == "Addfund":
        chat_id = call.message.chat.id
        qr , address= get_address_QR(chat_id)
        answerString = f'Your deposit address is \n{address}'
        await call.message.answer_photo(qr, caption=answerString, reply_markup=mainMenu)

    if call.data == "withdraw":
        text = 'Enter the withdraw address\nOr anything else to cancel'
        await withdrawForm.address.set()
        await call.message.answer(text)



    await call.answer()
    



@dp.callback_query_handler(text=["P10", "P20", "P50", "P70", "P90", "P100"])
async def long_short(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    buysize_mapping = {
        "P10": 1,
        "P20": 20,
        "P50": 50,
        "P70": 70,
        "P90": 90,
        "P100": 100,
    }
    buysize = buysize_mapping.get(call.data)
    # add buysize to dictionary
    orders_data[chat_id]['amount']= buysize


    #get order info
    order_type = orders_data[chat_id]['type']
    slippage = orders_data[chat_id]['slippage']
    

    

    reply_markup = create_buy_size_keyboard(order_type, buysize, '%',slippage)
    await bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(text=['other_size'])
async def other_size(call: types.CallbackQuery):
    text = 'Enter the size in %:'
    await Form.buy_size.set()
    await call.message.reply(text)



@dp.message_handler(state=Form.buy_size)
async def process_buy_size(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    buysize = message.text
    if check_value(buysize):
        orders_data[chat_id]['amount']= buysize        
        # add buysize to dictionary
        orders_data[chat_id]['amount']= buysize


        #get order info
        order_type = orders_data[chat_id]['type']
        slippage = orders_data[chat_id]['slippage']
      


        reply_markup = create_buy_size_keyboard(order_type,buysize, '%',slippage)
        await message.reply(f'size is {buysize}%', reply_markup=reply_markup)
        await state.finish()
    else:
        text = 'Select an integer value between 1 and 100:'
        reply_markup = create_buy_size_keyboard(None, '%')
        await message.answer(text, reply_markup=reply_markup)
        await state.finish()



# --------------------- select slippage ------------------------------

@dp.callback_query_handler(text=["slip2", "slip5", "slip10", "slip20", "slipmax"])
async def slipage(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    slip_mapping = {
        "slip2": 2,
        "slip5": 5,
        "slip10": 10,
        "slip20": 20,
        "slipmax": 100,
    }
    slip_size = slip_mapping.get(call.data)

    # add slippage to dictionary
    orders_data[chat_id]['slippage']= slip_size


    #get order info
    order_type = orders_data[chat_id]['type']    
    buysize = orders_data[chat_id]['amount']
    sizetype = '%'

    reply_markup = create_buy_size_keyboard(order_type,buysize, sizetype, slip_size)
    await bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(text=['other_slip'])
async def other_slip(call: types.CallbackQuery):
    text = 'Enter the slippage in %:'
    await Form.sipp_size.set()
    await call.message.reply(text)


@dp.message_handler(state=Form.sipp_size)
async def process_sipp_size(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    slip_size = message.text
    #get order info
    order_type = orders_data[chat_id]['type']    
    buysize = orders_data[chat_id]['amount']
    sizetype = '%'


    if check_value(slip_size):
        # add slippage to dictionary
        orders_data[chat_id]['slippage']= slip_size




        reply_markup = create_buy_size_keyboard(order_type, buysize, sizetype, slip_size)
        await message.reply(f'Slip size is {slip_size}%', reply_markup=reply_markup)
        await state.finish()
    else:
        text = 'Select an integer value between 1 and 100:'
        reply_markup = create_buy_size_keyboard(order_type,buysize, '%', None)
        await message.answer(text, reply_markup=reply_markup)
        await state.finish()



# -----------------------Execut_buy #-----------------------


@dp.callback_query_handler(text=['Execut_buy'])
async def execut_buy(call: types.CallbackQuery):
    text = 'Enter the contract to buy:'
    await Form.contract.set()
    await call.message.answer(text)

@dp.callback_query_handler(text=['Execut_sell'])
async def execut_buy(call: types.CallbackQuery):
    text = 'Enter the contract to sell:'
    await Form.contract.set()
    await call.message.answer(text)

# Handling incoming messages with contract information
@dp.message_handler(state=Form.contract)
async def process_contract(message: types.Message, state: FSMContext):
    # Get chat_id from the incoming message
    chat_id = message.chat.id

    # Extract the contract address from the incoming message
    contract = message.text

    # Finish the current state
    await state.finish()

    # TODO: Add a check here to validate the contract address (e.g., via a regular expression or API call)

    # Store the contract address in the orders_data dictionary
    orders_data[chat_id]['contract'] = contract
    # Extract orders_data
    buysize = orders_data[chat_id]['amount']
    slipage = orders_data[chat_id]['slippage']
    side = orders_data[chat_id]['type']


    if side == 'buy':
        print('buy')
        fromToken = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        toToken = contract
        # Get the balance of the wallet
        wallet_balance = get_ETH_balance(chat_id)
        # Convert wallet_balance and buysize to float for calculations
        wallet_balance = float(wallet_balance)
        buysize = float(buysize)

        # Calculate the buy amount based on wallet balance and buysize
        buy_amount = wallet_balance * (buysize / 100)
        orders_data[chat_id]['buy_amount'] = buy_amount


    elif side == 'sell':
        print('sell')
        fromToken = contract
        toToken = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        address , private_key  = get_address_key(chat_id)
        token_name, token_symbol, token_decimals, wallet_balance = get_token_balance(fromToken,address )
            
        # Convert wallet_balance and buysize to float for calculations
        wallet_balance = float(wallet_balance)
        buysize = float(buysize)
        print('wallet_balance :',wallet_balance)

        # Calculate the buy amount based on wallet balance and buysize
        buy_amount = wallet_balance * (buysize / 100)
        orders_data[chat_id]['buy_amount'] = buy_amount

    # Fetch quote information for the token swap
    quote = get_quote('42161', fromToken, toToken, buy_amount)
    print(quote)

    # Check if quote is not None
    if quote is not None:
        # Prepare text for the message
        text = f"""Swap {quote['swap']['fromTokenAmount']}{quote['fromToken']['symbol']} to {quote['swap']['toTokenAmount']}{quote['toToken']['symbol']}"""
        # Generate a confirm button
        reply_markup = confirm_button(text)

        # Reply with the processed information
        await message.reply(f'contract is {contract}\nbuy_size: {buysize}\nslippage: {slipage}\n--------------\n {text}',
                        reply_markup=reply_markup)
    
    else:
        text = "Failed to fetch quote. Please try again."

        reply_markup = mainMenu()
        await message.reply(text,
                        reply_markup=reply_markup)

    

@dp.callback_query_handler(text=['confirm_buy'])
async def confirm_buy(call: types.CallbackQuery):
    """
    Confirm the buy action in response to a callback query with the text 'confirm_buy'.
    
    Parameters:
    - call: types.CallbackQuery, the callback query object.
    """
    # Get chat ID to identify the user
    chat_id = call.message.chat.id
    
    # Get address and private key of the user
    address, private_key = get_address_key(chat_id)

    # Extract amount, slippage, and contract address from stored orders_data
    buysize = float(orders_data[chat_id]['amount'])  # Convert to float
    slippage = float(orders_data[chat_id]['slippage'])  # Convert to float
    contract = orders_data[chat_id]['contract']
    side = orders_data[chat_id]['type']
    buy_amount = orders_data[chat_id]['buy_amount']

    if side == 'buy':
        print('buy')
        fromToken = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        toToken = contract

    elif side == 'sell':
        print('sell')
        fromToken = contract
        toToken = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'


# Execute swap request
    response = requestSwap('42161', fromToken, toToken, address, buy_amount, slippage)

    # Extract fromToken and toToken symbols from the response
    fromToken = response['fromToken']['symbol']
    toToken = response['toToken']['symbol']

    # Notify user that the swap is in process
    reply_msg = f"Swap {fromToken} to {toToken} processing"
    print(f'Reply message: {reply_msg}')
    await call.message.reply(reply_msg)
    
    # Perform the swap and get the transaction hash
    tx_hash = swap(response, address, private_key)

    # Create and send transaction success reply with link to Arbiscan
    link = f'https://arbiscan.io/tx/{tx_hash}'
    reply_success = f'Transaction successful:\n{link}'
    await call.message.reply(reply_success)



# --------------------change wallet--------


@dp.callback_query_handler(text=['change_wallet'])
async def change_wallet_form(call: types.CallbackQuery):
    text = 'Enter the private key of your wallet\nOr anything else to cancel'
    await walletForm.wallet.set()
    await call.message.reply(text)


@dp.message_handler(state=walletForm.wallet)
async def process_wallet(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    private_key = message.text
    is_valid = change_wallet(chat_id, str(private_key))
    
    if is_valid:
        Message = "ajouter solde etc"
        await message.reply(f'Your Wallet was changed\n{Message}', reply_markup=mainMenu)
        await state.finish()
    else:
        print("La clé privée n'est pas valide.")
        await message.reply(f'No private key', reply_markup=mainMenu)
        await state.finish()




# --------------------withdraw from wallet-------

@dp.message_handler(state=withdrawForm.address)
async def process_wallet(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    
    withdraw_address = message.text
    print(withdraw_address,withdraw_address,withdraw_address,withdraw_address)
    is_valid = check_address(withdraw_address)
    

    if is_valid:
        withdraw_data[chat_id] = {'withdraw_address' : withdraw_address,
                                  'withdraws_size':''}
        print(withdraw_data)

        await message.reply(f'withdraw address: {withdraw_address}\n', reply_markup=withdrawMenu())
    else:
        await message.reply(f'No withdraw address', reply_markup=mainMenu)

    await state.finish()



@dp.callback_query_handler(text=["W10", "W20", "W50", "W70", "W90", "W100"])
async def withdraw_wallet(call: types.CallbackQuery, state: FSMContext):
    """Handles withdrawal amounts based on a predefined set of sizes."""

    chat_id = call.message.chat.id

    # Mapping between callback data and actual withdrawal sizes
    withdrawsSize_mapping = {
        "W10": 1,
        "W20": 20,
        "W50": 50,
        "W70": 70,
        "W90": 90,
        "W100": 100,
    }

    # Set the withdraw size for the current chat
    withdraws_size = withdrawsSize_mapping.get(call.data)

    withdraw_data[chat_id]['withdraws_size'] = withdraws_size
    print(withdraw_data)

    reply_markup = withdrawMenu(withdraws_size)

    await bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(text=['withdraw_other_size'])
async def withdraw_other_size(call: types.CallbackQuery):
    text = 'Enter the withdraw size in %:'
    await withdrawForm.withdraw_size.set()
    await call.message.reply(text)


@dp.message_handler(state=withdrawForm.withdraw_size)
async def process_withdraw_size(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    withdraws_size = message.text

    if check_value(withdraws_size):
        # add withdraws_size to dictionary
        withdraw_data[chat_id] = {'withdraws_size' : withdraws_size}


        reply_markup = withdrawMenu(withdraws_size)
        await message.reply(f'withdraws size is {withdraws_size}%', reply_markup=reply_markup)
    else:
        text = 'Select an integer value between 1 and 100:'
        reply_markup = withdrawMenu()
        await message.answer(text, reply_markup=reply_markup)
    await state.finish()



@dp.callback_query_handler(text='Continue_withdraw')
async def Continue_withdraw(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    withdraws_size = withdraw_data[chat_id]['withdraws_size']
    withdraw_address = withdraw_data[chat_id]['withdraw_address']

    # ajouter le calcul avec la valeur réel
    #--------------------

    Button_text = f'confirm withdraw of {withdraws_size}'

    reply_markup = continue_withdraw(Button_text)
    
    await bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=reply_markup
    )



@dp.callback_query_handler(text='confirm_withdraw')
async def Continue_withdraw(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    withdraws_size = withdraw_data[chat_id]['withdraws_size']
    withdraw_address = withdraw_data[chat_id]['withdraw_address']

    session = Session()
        
    # Récupérer l'utilisateur à partir de chat_id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    private_key = user.private_key
    address = user.address

    session.close()

    withdraw_address = withdraw_data[chat_id]['withdraw_address']
 
    await call.message.reply("transaction send")

    tx_hash = send_transaction(address, withdraw_address,1,private_key)

    link = f'https://arbiscan.io/tx/{tx_hash}'
    reply = f'Transaction successful:\n{link}'
    await call.message.reply(reply)




def start_polling():
    executor.start_polling(dp, skip_updates=True)





