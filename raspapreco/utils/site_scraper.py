import time

import requests
from bs4 import BeautifulSoup

import raspapreco.localizations

SCRAPY_DICT = \
    {'aliexpress': {'url': 'https://pt.aliexpress.com/wholesale',
                 'param_names': {'categoria': 'catId', 'descricao': 'SearchText'},
                 'xpath': None,
                 'target': ('span', {'class': 'value', 'itemprop': 'price'})
                 },
     'other': {'url': 'https://',
               'xpath': 'XPATH',  # or
               'target': ('a', {'class': 'xxx', 'id': 'xxx', '...': 'xxx'})
               }
     }


class Scraper:
    '''Receives sites and produtos, call necessary functions,
    do error management and store resuls'''

    def __init__(self, sites=None, produtos=None):
        self.sites = sites
        self.produtos = produtos
        self.scraped = {}

    def scrap(self):
        # TODO: use non blocking (async or threaded call)
        if self.sites is None:
            raise AttributeError(_('No site passed'))
        if self.produtos is None:
            raise AttributeError(_('No site passed'))
        for produto in self.produtos:
            produtos_scrapy = {}
            for site in self.sites:
                produtos_scrapy[site.title] = scrap_one(site, produto)
            self.scraped[produto.descricao] = produtos_scrapy
            time.sleep(0.1)  # Prevent site blocking


def scrap_one(site, produto):
    # TODO: use non blocking (async or threaded call)
    configs = SCRAPY_DICT.get(site.title)
    if not configs:
        raise KeyError(_('Site not configured: ' + site.title))
    url = configs['url']
    xpath = configs['xpath']
    search_params = configs['param_names']
    search = {}
    search[search_params['descricao']] = produto.descricao
    target = configs['target']
    target_name = target[0]
    target_atributes = target[1]

    html = requests.get(url, params=search)
    bs = BeautifulSoup(html.text, "html.parser")
    if xpath:
        pass  # TODO: implementar busca por XPATH
    else:
        name_list = bs.findAll(target_name, target_atributes)

    rows = [row.getText() for row in name_list]
    return rows


def extrai_valor(texto):
    pos_real = texto.find('R$')
    if pos_real == -1:
        pos_real = 0
    else:
        pos_real += 3
    pos_hifen = texto.find('-')
    if pos_hifen == -1:
        pos_hifen = len(texto)
    texto = texto[pos_real:pos_hifen]
    texto = texto.replace(',', '.')
    return float(texto)


def make_floatlist(str_list):
    '''Receives a list of strings, parses into a list of floats'''
    list_float = []
    sum = 0
    for item in str_list:
        value = extrai_valor(item)
        list_float.append(value)
        sum += value
    return list_float, sum
