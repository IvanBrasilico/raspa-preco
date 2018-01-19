import unittest
from datetime import datetime

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, ProdutoEncontrado, Site)
from raspapreco.utils.dossie_manager import DossieManager

mysession = MySession(Base, test=True)
session = mysession.session()
engine = mysession.engine()
Base.metadata.create_all(engine)


class TestExecutor(unittest.TestCase):
    executor = None

    def __init__(self, *args, **kwargs):
        self.executor = None
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        procedimento = Procedimento('teste')
        session.add(procedimento)
        session.commit()
        dossie = Dossie(procedimento, datetime.now())
        session.add(dossie)
        session.commit()
        produto = Produto('produto', 1.99)
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
        TestExecutor.executor = DossieManager(
            session, procedimento=procedimento, dossie=dossie
        )

    def tearDown(self):
        Base.metadata.drop_all(engine)

    def test_executor(self):
        html = TestExecutor.executor.dossie_to_html_table()
        assert html is not None
