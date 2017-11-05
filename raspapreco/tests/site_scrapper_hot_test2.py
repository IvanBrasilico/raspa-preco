import unittest
from datetime import date

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, ProdutoEncontrado, Site)
from raspapreco.utils.site_scraper import Scraper, extrai_valor

mysession = MySession(Base, test=True)
session = mysession.session()
engine = mysession.engine()
Base.metadata.create_all(engine)


class TestScrap(unittest.TestCase):
    def set_up(self):
        proc = session.query(Procedimento).filter(
            Procedimento.nome == 'testeQWERTY').first()
        if proc is None:
            print('Procedimento não existe, criando...')
            proc = Procedimento('testeQWERTY')
            session.add(proc)
            session.commit()

        if not proc.produtos:
            ali = session.query(Site).filter(
                Site.title == 'aliexpress').first()
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

    def tear_down(self):
        proc = session.query(Procedimento).filter(
            Procedimento.nome == 'testeQWERTY').first()
        session.delete(proc)
        session.commit()

    def test_hot_scrap(self):
        self.set_up()
        proc = session.query(Procedimento).filter(
            Procedimento.nome == 'testeQWERTY').first()
        scrap = Scraper(proc.sites, proc.produtos)
        scrap.scrap()
        # print(scrap.scraped)
        assert scrap.scraped != []
        dossie = Dossie(proc, date.today())
        session.add(dossie)
        session.commit()
        for produto, d in scrap.scraped.items():
            produto = session.query(Produto).filter(
                Produto.id == produto).first()
            for site, campos in d.items():
                site = session.query(Site).filter(
                    Site.id == site).first()
                for ind in range(len(campos['url'])):
                    produtoencontrado = ProdutoEncontrado(
                        dossie,
                        produto,
                        site,
                        descricao_site=campos['descricao'][ind],
                        url=campos['url'][ind],
                        preco=extrai_valor(campos['preco'][ind])
                    )
                    session.add(produtoencontrado)
        session.commit()

        self.tear_down()
