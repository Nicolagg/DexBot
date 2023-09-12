from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    address = Column(String, nullable=True)
    private_key = Column(String, nullable=True)
    #tokens = relationship("Token", back_populates="user")
    #orders = relationship("SwapOrder", back_populates="user")

    def __repr__(self):
        return f"<User(chat_id={self.chat_id})>"
    


# class Token(Base):
#     __tablename__ = 'tokens'
    
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     abbreviation = Column(String, nullable=False)
#     blockchain = Column(String, nullable=False)
#     contract_address = Column(String, nullable=False) # Nouveau champ pour l'adresse du contrat
#     num_digits = Column(Integer, nullable=False)
    
#     def __repr__(self):
#         return f"<Token(name={self.name}, abbreviation={self.abbreviation})>"
    
#     def get_token_info(self, web3):
#         """
#         Retrieve token information from the blockchain.
        
#         :param web3: A Web3 instance to interact with the Ethereum blockchain.
#         :return: Updated token name, symbol, and decimals from the blockchain.
#         """
#         abi = [
#             # ... (same as the original ABI you've defined)
#         ]
        
#         address = Web3.toChecksumAddress(self.contract_address)
#         contract = web3.eth.contract(address=address, abi=abi)
        
#         self.name = contract.functions.name().call()
#         self.abbreviation = contract.functions.symbol().call()
#         self.num_digits = contract.functions.decimals().call()
        
#         return self.name, self.abbreviation, self.num_digits



# class SwapOrder(Base):
#     __tablename__ = 'swap_orders'
    
#     id = Column(Integer, primary_key=True)
#     amount = Column(Float, nullable=False)
#     slippage = Column(Float, nullable=False)
#     sell_token_address = Column(String, nullable=False)
#     buy_token_address = Column(String, nullable=False)
#     chat_id = Column(Integer, ForeignKey('users.chat_id'))
    
#     user = relationship("User", back_populates="orders")
    
#     def __repr__(self):
#         return f"<SwapOrder(amount={self.amount}, slippage={self.slippage})>"


