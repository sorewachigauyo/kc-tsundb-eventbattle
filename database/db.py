from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from data.config import db_address

Base = declarative_base()
engine = create_engine(db_address)
Session = sessionmaker(bind=engine)

def init_db():
    from database.models import Battle, Attack, Fleet, LBAS, PlayerShip
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
