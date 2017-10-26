import unittest
from unittest import mock

import requests_mock

from raspapreco.utils.site_scraper import Scraper, make_floatlist


class TestModel(unittest.TestCase):
    def test_make_floatlist(self):
        test_list = ['R$ 27,45', '2.5', 'R$ 120,0 - 180']
        assert_list = [27.45, 2.5, 120.]
        result_list, sum = make_floatlist(test_list)
        assert result_list == assert_list
        assert sum == 149.95

    # @mock.patch('raspapreco.utils.site_scraper.requests')
    @requests_mock.mock()
    def test_Scraper(self, mocker):
        # html = type('Html', (object, ), {'text': '<span class="value" itemprop="price">21,45</a>'})
        # requests.get.return_value.html = html
        mocker.get(requests_mock.ANY,
                   text='<span class="value" itemprop="price">21,45</a>' +
                   '<span class="value" itemprop="price">22,56</a>')
        site = type('Site', (object, ), {'title': 'nowhere'})
        produto = type('Produto', (object, ), {'descricao': 'bolsa'})
        sites = [site]
        produtos = [produto]
        scrap = Scraper()
        self.assertRaises(AttributeError, scrap.scrap)
        scrap = Scraper(sites)
        self.assertRaises(AttributeError, scrap.scrap)
        scrap = Scraper(sites, produtos)
        self.assertRaises(KeyError, scrap.scrap)
        site.title = 'aliexpress'
        scrap = Scraper(sites, produtos)
        scrap.scrap()
        assert scrap.scraped.get(produto.descricao) is not None
        result = scrap.scraped.get(produto.descricao).get(site.title)
        assert result is not None
        assert result == ['21,45', '22,56']
