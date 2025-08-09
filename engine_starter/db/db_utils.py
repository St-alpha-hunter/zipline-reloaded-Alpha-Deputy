import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base

load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)

def create_tables():
    Base.metadata.create_all(engine)

def upsert_asset(session, asset_data):
    """
    asset_data: dict with keys like symbol, start_date, end_date, exchange, auto_close_date
    """
    from db.models import Asset

    existing = session.query(Asset).filter_by(symbol=asset_data["symbol"]).first()
    if existing:
        for k, v in asset_data.items():
            setattr(existing, k, v)
    else:
        new_asset = Asset(**asset_data)
        session.add(new_asset)