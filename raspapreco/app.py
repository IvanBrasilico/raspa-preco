from sqlalchemy.orm import sessionmaker

from models.models import Procedimento, Produto, Site, engine
from utils.site_scraper import Scraper

Session = sessionmaker(bind=engine)
session = Session()


proc = session.query(Procedimento).filter(Procedimento.nome == 'teste').first()
if proc is None:
    print('Procedimento não existe, criando...')
    proc = Procedimento('teste')
    session.add(proc)
    session.commit()


if not proc.produtos:
    ali = session.query(Site).filter(Site.title == 'aliexpress').first()
    if ali is None:
        print('Site não existe, criando...')
        ali = Site('aliexpress', 'https://pt.aliexpress.com')
        proc.sites.append(ali)

    bolsa = session.query(Produto).filter(
        Produto.descricao == 'bolsa feminina').first()
    if bolsa is None:
        print('Bolsa não existe, criando...')
        bolsa = Produto('bolsa feminina')
        proc.produtos.append(bolsa)

    caneta = session.query(Produto).filter(
        Produto.descricao == 'Caneta de 10 cores').first()
    if caneta is None:
        print('Caneta não existe, criando...')
        caneta = Produto('Caneta de 10 cores')
        proc.produtos.append(caneta)

    session.merge(proc)
    session.commit()


scrap = Scraper(proc.sites, proc.produtos)

scrap.scrap()

print(scrap.scraped)
