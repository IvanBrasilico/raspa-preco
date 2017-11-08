import unittest

import requests_mock

from raspapreco.utils.site_scraper import Scraper, make_floatlist


class TestModel(unittest.TestCase):
    def test_make_floatlist(self):
        test_list = ['R$ 27,45', '2.50', '2,70', 'R$ 120,0 - 180',
                     'R$ 4.977,17', 'R$ 60,62  - R$ 65,00', '20,18 ']
        assert_list = [27.45, 2.5, 2.7, 120., 4977.17, 60.62, 20.18]
        result_list, sum = make_floatlist(test_list)
        assert result_list == assert_list
        assert sum == 5210.62

    # @mock.patch('raspapreco.utils.site_scraper.requests')
    @requests_mock.mock()
    def test_Scraper(self, mocker):
        # html = type('Html', (object, ),
        #  {'text': '<span class="value" itemprop="price">21,45</a>'})
        # requests.get.return_value.html = html
        mocker.get(requests_mock.ANY,
                   text='<span class="value" itemprop="price">21,45</a>' +
                   '<span class="value" itemprop="price">22,56</a>')
        site = type('Site', (object, ), {
                    'id': '1', 'title': 'nowhere', 'targets': None})
        site_com_targets = \
            type('Site', (object, ),
                 {
                'id': '1',
                'title': 'aliexpress',
                'targets': {
                    'preco': ('span', {'class': 'value', 'itemprop': 'price'})}
            })
        produto = type('Produto', (object, ), {
                       'id': '2', 'descricao': 'bolsa feminina'})
        sites = [site]
        produtos = [produto]
        scrap = Scraper()
        self.assertRaises(AttributeError, scrap.scrap)
        scrap = Scraper(sites)
        self.assertRaises(AttributeError, scrap.scrap)
        scrap = Scraper(sites, produtos)
        self.assertRaises(KeyError, scrap.scrap)
        site.title = 'aliexpress'
        sites.append(site_com_targets)
        scrap = Scraper(sites, produtos)
        scrap.scrap()
        assert scrap.scraped.get(produto.id) is not None
        result = scrap.scraped.get(produto.id).get(site.id).get('preco')
        assert result is not None
        assert result == ['21,45', '22,56']
