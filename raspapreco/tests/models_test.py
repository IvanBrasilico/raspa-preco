import unittest
from datetime import date

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, ProdutoEncontrado, Site)


class TestModel(unittest.TestCase):
    def setUp(self):
        mysession = MySession(Base, test=True)
        self.session = mysession.session()
        self.engine = mysession.engine()
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_procedimento(self):
        procedimento = Procedimento('teste')
        assert procedimento.nome == 'teste'
        self.session.commit()
        # assert procedimento.id is not None

    def test_site(self):
        site = Site('teste', 'url')
        assert site.title == 'teste'
        assert site.url == 'url'
        site.targets = {'1': 1, '2': 2}
        self.session.add(site)
        self.session.commit()
        assert site.targets['1'] == 1
        assert site.targets['2'] == 2
        # assert site.id is not None

    def test_produto(self):
        produto = Produto('teste', 1.99)
        assert produto.descricao == 'teste'
        self.session.commit()
        # assert produto.id is not None

    def test_vincula_produto(self):
        procedimento = Procedimento('teste')
        assert procedimento.nome == 'teste'
        procedimento.id = 1  # Memory does not have autoincrement
        self.session.commit()
        produto = Produto('teste', 1.99)
        assert produto.descricao == 'teste'
        produto.id = 1  # Memory does not have autoincrement
        produto2 = Produto('teste2', 2.99)
        assert produto2.descricao == 'teste2'
        produto2.id = 2  # Memory does not have autoincrement
        self.session.commit()
        procedimento.produtos.append(produto)
        self.session.commit()
        assert len(procedimento.produtos) == 1
        procedimento.produtos.append(produto2)
        self.session.commit()
        assert len(procedimento.produtos) == 2
        assert procedimento.produtos[0] == produto
        assert procedimento.produtos[1] == produto2
        procedimento.produtos.remove(produto)
        self.session.commit()
        assert len(procedimento.produtos) == 1

    def test_dossie(self):
        procedimento = Procedimento('teste')
        data = date(2017, 10, 31)
        dossie = Dossie(procedimento, data)
        self.session.commit()
        assert dossie.procedimento_id == procedimento.id
        assert dossie.data == data

    def test_produtoencontrado(self):
        procedimento = Procedimento('teste')
        dossie = Dossie(procedimento, '2017-10-31')
        produto = Produto('teste', 1.99)
        site = Site('teste', 'url')
        produtoencontrado = ProdutoEncontrado(
            dossie, produto, site, 'teste', 'www.teste', 1.00)
        self.session.add(produtoencontrado)
        self.session.commit()
        assert produtoencontrado.dossie_id == dossie.id
        assert produtoencontrado.descricao_site == 'teste'
        assert produtoencontrado.url == 'www.teste'
        assert produtoencontrado.preco == 1.00
        produtoencontrado.campos = {'1': 1, '2': 2}
        self.session.merge(produtoencontrado)
        self.session.commit()
        assert produtoencontrado.campos['1'] == 1
        assert produtoencontrado.campos['2'] == 2
