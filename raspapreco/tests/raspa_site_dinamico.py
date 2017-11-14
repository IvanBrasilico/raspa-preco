import sys

from raspapreco.models.models import Base, MySession, Target, Site
from raspapreco.utils.site_scraper import scrap_one

if __name__ == '__main__':
    debug = False
    if len(sys.argv) > 1:
        debug = 'debug'.find(sys.argv[1]) != -1

    mysession = MySession(Base, test=True)
    session = mysession.session()
    engine = mysession.engine()
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    site = session.query(Site).filter(
        Site.title == 'aliexpressdinamico').first()

    if not site:
        print('Criando novo')
        site = Site('aliexpressteste', 'https://aliexpress.com/wholesale')
        session.add(site)

    site.params_names = {'descricao': 'SearchText'}
    
    target1 = Target('preco', 'span', '{"class": "value", "itemprop": "price"}')
    target2 = Target('unidade', 'span', '{"class": "unit"}')
    target3 = Target('url', 'span', '{"class": "history-item product "}', getter='href')
    target4 = Target('descricao', 'span', '{"class": "history-item product "}')
    
    site.targets = [target1, target2, target3, target4]
    print(site.targets)
    session.merge(site)
    session.commit()
    print(site.targets)

    produto = type('Produto', (object, ), {
        'id': '2', 'descricao': 'bolsa feminina'})

    scraped = scrap_one(site, produto, debug=debug)
    for key, value in scraped.items():
        print(key, value)
