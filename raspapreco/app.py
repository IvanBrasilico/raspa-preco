from sqlalchemy.orm import sessionmaker

from models.models import engine

Session = sessionmaker(bind=engine)
session = Session()
