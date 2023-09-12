from web3 import Web3
import os
import yaml
import qrcode
from io import BytesIO
from database import Session
from models import User
import requests
import json




with open('connection.yaml', 'r') as f: 
    connection = yaml.safe_load(f)


API_TOKEN= connection['infura']['API_TOKEN']




# Create a Web3 instance (assuming it's already connected to an Ethereum node)
infura_url = f'https://arbitrum-mainnet.infura.io/v3/{API_TOKEN}'
w3 = Web3(Web3.HTTPProvider(infura_url))



def generate_address():
    """
    Generates a random Ethereum address and its corresponding private key.

    Returns:
    - tuple: A tuple containing the private key and the Ethereum address as strings.
    """
     # Generate a random 32-byte private key in hexadecimal format
    private_key = os.urandom(32).hex()

    # Calculate the corresponding Ethereum address from the private key
    address = w3.eth.account.from_key(private_key).address

    return private_key, address

    

def check_address(address):  
    """
    Verify if the given Ethereum address is a valid checksum address.
    
    Parameters:
    address (str): The Ethereum address to be verified.
    
    Returns:
    bool: True if the address is a valid checksum address, False otherwise.
    """

    try:      

        ChecksumAddress = w3.is_checksum_address(address)

        return  ChecksumAddress
    
    except Exception as e:
        print(f"Erreur lors de la validation de la clé privée : {str(e)}")
        return False




def change_wallet(chat_id, private_key):  
    """
    Change the wallet information of a user in the database.
    
    Parameters:
        chat_id (str): The chat ID of the user to update.
        private_key (str): The new private key for the user.
    
    Returns:
        bool: True if the operation is successful and the address is a valid checksum address. False otherwise.
    """

    try:
        # Generate the Ethereum address from the given private key
        address = w3.eth.account.from_key(str(private_key)).address  
        
        # Validate that the generated address is a checksum address
        ChecksumAddress = w3.is_checksum_address(address)
        
        # Initialize a new database session
        session = Session()

        if ChecksumAddress:
            # Find the user by chat_id in the database
            user = session.query(User).filter_by(chat_id=chat_id).first()
            
            # If the user exists, update their private_key and address fields
            if user:
                user.private_key = private_key
                user.address = address

                # Commit the changes to the database and close the session
                session.commit()
                session.close()
                return ChecksumAddress
            else:
                # If no user with the specified chat_id is found
                print("User with the specified chat_id not found.")
                session.close()
                return False
        else:
            # If the address is not a valid checksum address
            print("The address is not a valid checksum address.")
            session.close()
            return False
    
    except Exception as e:
        # Catch any exceptions and print an error message
        print(f"Erreur lors de la validation de la clé privée : {str(e)}")
        session.close()
        return False

    

def get_address_QR(chat_id):
    """
    Generate a QR code for a user's address based on the user's chat_id.

    Parameters:
        chat_id (str): The chat ID of the user.

    Returns:
        tuple: A tuple containing the binary data of the QR code image and the address.
        None: Returns None if the user is not found or an error occurs.
    """
    try:
        # Initialize database session
        session = Session()

        # Retrieve the user from the database using the chat_id
        user = session.query(User).filter_by(chat_id=chat_id).first()

        # If the user exists, proceed to generate QR code for their address
        if user:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            address = user.address
            qr.add_data(address)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")

            # Save the image in a memory stream
            image_stream = BytesIO()
            qr_image.save(image_stream, format='PNG')

            # Retrieve the binary data of the image
            image_bytes = image_stream.getvalue()
            
            # Close the session
            session.close()

            return image_bytes, address

        else:
            print("User with the specified chat_id not found.")
            session.close()
            return None
    except Exception as e:
        print(f"Error while retrieving the address: {str(e)}")
        session.close()
        return None
    


def get_address_key(chat_id):
    """
    Retrieve the address and private key of a user based on chat_id.
    
    Parameters:
        chat_id (int or str): The unique identifier for the chat/user.
    
    Returns:
        tuple: Returns a tuple containing the address and private key of the user if found,
               otherwise returns None.
    """
    try:
        # Create a new SQLAlchemy session
        session = Session()
        
        # Retrieve the user object from the database that matches the given chat_id
        user = session.query(User).filter_by(chat_id=chat_id).first()

        # If the user exists, return their address and private key
        if user:
            address = user.address
            private_key = user.private_key
          
            # Close the session and return the address and private key
            session.close()
            return address, private_key
        
        else:
            # Log a message if the user is not found and close the session
            print("User with the specified chat_id not found.")
            session.close()
            return None

    except Exception as e:
        # Log the exception and close the session
        print(f"Error while retrieving the address: {str(e)}")
        session.close()
        return None


def get_fee(tx):
    """
    Calculates the gas fees for a given transaction.
    
    Parameters:
    - tx: The transaction for which to estimate the gas fee.
    
    Returns:
    - max_priority_fee_per_gas: The maximum priority fee per gas.
    - fee_per_gas: The fee per gas based on the latest block's base fee.
    - estimate_gas: The estimated gas needed for the transaction.
    """
    
    # Fetch the current gas price from the network
    gas_price = w3.eth.gas_price
    
    # Calculate the maximum priority fee per gas by multiplying current gas price with a factor
    # The factor (1.5 here) can be adjusted based on your specific needs
    max_priority_fee_per_gas = int(gas_price * 1.5)
    
    # Get the latest block number and its details
    latest_block_number = w3.eth.block_number
    latest_block = w3.eth.get_block(latest_block_number)
    
    # Extract the base fee per gas from the latest block
    fee_per_gas = latest_block['baseFeePerGas']
    
    # Estimate the gas required for the transaction
    estimate_gas = w3.eth.estimate_gas(tx)
    
    return max_priority_fee_per_gas, fee_per_gas, estimate_gas



def get_ETH_balance(chat_id):
    """
    Fetches the balance of an Ethereum address associated with a chat ID.
    
    Parameters:
    - chat_id: The chat ID for which to fetch the balance.
    
    Returns:
    - The balance of the Ethereum address.
    """
    session = Session()
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user is not None:
        address = user.address  # get user address
        balance_wei = w3.eth.get_balance(address)
        balance_eth = balance_wei * 10**-18
        session.close()
        return balance_eth
    else:
        session.close()
        return None  # Handle the case where the user is not found
    



def send_transaction(user_address, to_address, value, private_key, data=''):
    """
    Sends an Ethereum transaction.
    
    Parameters:
    - user_address: The address from which to send the transaction.
    - to_address: The address to which to send the transaction.
    - value: The amount to send.
    - private_key: The private key for signing the transaction.
    - data: Optional data for the transaction.
    """
    # Create the initial transaction dictionary
    tx = {
        'from': w3.to_checksum_address(user_address),
        'to': w3.to_checksum_address(to_address),
        'value': int(value),
        'chainId': 42161,
        'data': data
    }
    
    # Fetch the gas fee information
    max_priority_fee_per_gas, fee_per_gas, estimate_gas = get_fee(tx)
    
    # Fetch the nonce
    nonce = w3.eth.get_transaction_count(user_address)
    
    # Update the transaction dictionary with fee and nonce details
    tx.update({
        'nonce': nonce,
        'maxPriorityFeePerGas': fee_per_gas,
        'maxFeePerGas': max_priority_fee_per_gas,
        'gas': estimate_gas
    })

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(tx, private_key)
    
    # Send the transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    return txn_hash.hex()



def get_token_info(contract_address):
    """
    Fetches and returns the name, symbol, and decimal count of a token with the given contract address.

    Parameters:
        contract_address (str): The contract address of the token.

    Returns:
        tuple: The name, symbol, and decimal count of the token.
    """

    # Define ABI (Application Binary Interface) for ERC20 Token
    # This defines how to interact with the contract's functions
    abi = [
        {
            "inputs": [],
            "name": "name",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "symbol",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    # Convert the contract address to its checksummed version
    # This is necessary for interacting with the Ethereum network
    address = Web3.to_checksum_address(contract_address)
    
    # Create a contract object for interaction
    contract = w3.eth.contract(address=address, abi=abi)
    
    # Fetch the token information by calling the respective functions in the contract
    token_name = contract.functions.name().call()
    token_symbol = contract.functions.symbol().call()
    token_decimals = contract.functions.decimals().call()

    return token_name, token_symbol, token_decimals

def get_token_balance(contract_address, account_address):
    """
    Get details and balance of a specific ERC20 token for a given Ethereum account.
    
    Parameters:
    - contract_address (str): The Ethereum address of the token contract.
    - account_address (str): The Ethereum address of the account whose balance you want to check.
    
    Returns:
    - tuple: A tuple containing the token name, token symbol, token decimals, and account balance.
    """
    
    # Define the ABI (Application Binary Interface) for interacting with the smart contract
    abi = [
        {
            "inputs": [],
            "name": "name",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "symbol",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]

    # Convert the address to checksum format
    address = Web3.to_checksum_address(contract_address)
    
    # Create a contract object
    contract = w3.eth.contract(address=address, abi=abi)

    # Fetch token details
    token_name = contract.functions.name().call()
    token_symbol = contract.functions.symbol().call()
    token_decimals = contract.functions.decimals().call()

    # Get the balance of the account
    balance = contract.functions.balanceOf(Web3.to_checksum_address(account_address)).call()
    
    return token_name, token_symbol, token_decimals, balance * 10**-token_decimals


def get_quote(chain_id, fromTokenAddress, toTokenAddress, amount_human):
    """
    Fetches and returns quote information for a token swap from the 1inch API.

    Parameters:
        chain_id (int): The chain ID for the network.
        fromTokenAddress (str): The address of the token to swap from.
        toTokenAddress (str): The address of the token to swap to.
        amount_human (float): The amount to swap in human-readable form (not wei).

    Returns:
        dict: Information about the token swap, including token details and amounts.
    """

    # Handle Ethereum native asset 'ETH' case
    if fromTokenAddress == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
        fromToken_symbol = 'ETH'
        fromToken_name = 'Ethereum'
        fromToken_decimals = 18

        # Fetch token information for 'toTokenAddress'
        toToken_name, toToken_symbol, toToken_decimals= get_token_info(toTokenAddress)
    else:
        # Fetch token information for 'fromTokenAddress'
        fromToken_name, fromToken_symbol, fromToken_decimals= get_token_info(fromTokenAddress)
        toToken_name = 'Ethereum'
        toToken_symbol = 'ETH'
        toToken_decimals = 18
    
    # Convert the human-readable amount to its smallest unit (e.g., wei for ETH)
    amount = int(amount_human * (10 ** fromToken_decimals))

    # Define the API endpoint and headers

    headers = {
        "Authorization": "Bearer xT7Yht6XjpqoOtVf5fXTpYqNDIAhmHIt"  # Replace YOUR-API-KEY with your actual API key
        }
    
    # Build the 1inch API URL
    url = f'https://api.1inch.dev/swap/v5.2/{chain_id}/quote?src={fromTokenAddress}&dst={toTokenAddress}&amount={amount}'
 
    # Fetch the quote from the 1inch API
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON data
        res = response.json()
        print('---------------------------', res)
         
        
        print(toToken_name, toToken_symbol, toToken_decimals)

        # Prepare and return the token swap information
        dic = {
            'fromToken': {
                'symbol': fromToken_symbol,
                'name': fromToken_name,
                'decimals': fromToken_decimals
            },
            'toToken': {
                'symbol': toToken_symbol,
                'name': toToken_name,
                'decimals': toToken_decimals
            },
            'swap': {
                'fromTokenAmount': amount_human,
                'toTokenAmount': int(res['toAmount']) / (10 ** toToken_decimals) 
            }
        }
        
        return dic
    
    else:
        # Handle errors
        print(f"Failed to get data: {response.status_code}")

        try:
            error_data = response.json()
            print(f"Error message: {error_data.get('error', 'Unknown error')}")
            print(f"Error description: {error_data.get('description', 'No description provided')}")
            print(f"Request ID: {error_data.get('requestId', 'No request ID')}")
            print(f"Meta: {json.dumps(error_data.get('meta', {}), indent=4)}")

            return None

        except json.JSONDecodeError:
            print("Could not decode the error message from the server.")
            return None


def requestSwap(chain_id, fromTokenAddress, toTokenAddress, user_address, amount_human, slippage):
    """
    Request a token swap from 1inch API.

    Parameters:
    - chain_id: str, the blockchain network ID
    - fromTokenAddress: str, the address of the token to swap from
    - toTokenAddress: str, the address of the token to swap to
    - user_address: str, the user's blockchain address
    - amount_human: float, the amount of tokens to swap in human-readable form
    - slippage: float, the maximum slippage allowed

    Returns:
    - dict, the API response
    """
    # Log the address of the token being swapped from
    print(f'fromTokenAddress: {fromTokenAddress}')

    # Determine decimals based on the token address
    if fromTokenAddress == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
        decimals = 18  # Ethereum
    else:
        _, _, decimals = get_token_info(fromTokenAddress)

    # Convert the human-readable amount to its smallest unit
    amount = int(amount_human * 10 ** decimals)
    print(f'Amount in smallest unit: {amount}')

    # Construct the API URL
    url = f'https://api.1inch.dev/swap/v5.2/{chain_id}/swap?src={fromTokenAddress}&dst={toTokenAddress}&amount={amount}&from={user_address}&slippage={slippage}&includeTokensInfo=true'
    print(f'API Request URL:\n{url}')

    # Define the API endpoint and headers
    headers = {
        "Authorization": "Bearer xT7Yht6XjpqoOtVf5fXTpYqNDIAhmHIt"  # Replace with your actual API key
    }

    # Make the API request and capture the response
    response = requests.get(url, headers=headers)




    # Basic Error Handling
    if response.status_code != 200:
        print(f'Error: Received status code {response.status_code}')
        return None
    else:        

        json_response = response.json()  

        return json_response



# Perform the actual swap
def swap(requestSwap, user_address, private_key):
    # Commented-out code: error-handling could go here
    # ...
    
    # Extract necessary fields from the API response
    to_address = requestSwap['tx']['to']
    value = int(requestSwap['tx']['value'])
    data = requestSwap['tx']['data']

    # Log transaction details for debugging
    print(f'Value:\n{value}')
    print(f'----------------\nData:\n{data}')

    # Send the transaction and get the transaction hash
    tx_hash = send_transaction(user_address, to_address, value, private_key, data)
    return tx_hash