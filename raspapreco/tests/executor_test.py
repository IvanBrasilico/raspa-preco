import unittest
from datetime import date

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, ProdutoEncontrado, Site)
from raspapreco.utils.executor import Executor

mysession = MySession(Base, test=True)
session = mysession.session()
engine = mysession.engine()
Base.metadata.create_all(engine)


class TestExecutor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.executor = None
        unittest.TestCase.__init__(self, *args, **kwargs)

    def set_up(self):
        procedimento = Procedimento('teste')
        session.add(procedimento)
        session.commit()
        dossie = Dossie(procedimento, date.today())
        session.add(dossie)
        session.commit()
        produto = Produto('produto')
        session.add(produto)
        session.commit()
        site = Site('site', 'http')
        session.add(site)
        session.commit()
        produtoencontrado = ProdutoEncontrado(
            dossie,
            produto,
            site,
            'produtosite',
            'url',
            1.00)
        session.add(produtoencontrado)
        session.commit()
        self.executor = Executor(session, dossie=dossie)

    def tear_down(self):
        Base.metadata.drop_all(engine)

    def test_executor(self):
        self.set_up()
        html = self.executor.dossie_to_html_table()

        assert html is not None
