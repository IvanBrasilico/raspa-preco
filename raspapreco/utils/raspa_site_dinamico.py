import sys
from raspapreco.models.models import (Base, MySession, Site)
from raspapreco.utils.site_scraper import scrap_one

debug = False
if len(sys.argv) > 1:
    debug = 'debug'.find(sys.argv[1]) != -1



mysession = MySession(Base)
session = mysession.session()

site = session.query(Site).filter(Site.title == 'aliexpressdinamico').first()

if not site:
    print('Criando novo')
    site = Site('aliexpressdinamico', 'https://aliexpress.com/wholesale')
    session.add(site)

site.targets = {'preco': ('span', {'class': 'value', 'itemprop': 'price'}),
                'unit': ('span', {'class': 'unit'}),
                'url': ('a', {'class': 'history-item product '}, 'href'),
                'descricao': ('a', {'class': 'history-item product '})
                }
session.merge(site)
session.commit()
print(site)

produto = type('Produto', (object, ), {
    'id': '2', 'descricao': 'bolsa feminina'})

scraped = scrap_one(site, produto, debug=debug)
for key, value in scraped.items():
    print(key, value)
