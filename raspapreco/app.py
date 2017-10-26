from sqlalchemy.orm import sessionmaker

from models.models import engine, Produto, Site
from utils.site_scraper import Scraper

Session = sessionmaker(bind=engine)
session = Session()


ali = session.query(Site).filter(Site.title == 'aliexpress').first()
if ali is None:
    ali = Site('aliexpress', 'https://pt.aliexpress.com')
    session.commit()

bolsa = session.query(Produto).filter(Produto.descricao == 'bolsa feminina').first()
if bolsa is None:
    bolsa = Produto('bolsa feminina')
    session.commit()

scrap = Scraper([ali], [bolsa])

scrap.scrap()

print(scrap.scraped)
