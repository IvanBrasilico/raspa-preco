from sqlalchemy.orm import sessionmaker
from models.models import engine, Procedimento

Session = sessionmaker(bind=engine)
session = Session()
