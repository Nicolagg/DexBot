from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URI = 'sqlite:///crypto_bot.db'  
engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)