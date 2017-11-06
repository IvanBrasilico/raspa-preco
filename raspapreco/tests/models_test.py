import unittest
from datetime import date

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, ProdutoEncontrado, Site)


class TestModel(unittest.TestCase):
    def set_up(self):
        mysession = MySession(Base, test=True)
        self.session = mysession.session()
        self.engine = mysession.engine()
        Base.metadata.create_all(self.engine)

        """self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.Base = declarative_base()
        self.Base.metadata.create_all(self.engine)
        """

    def tear_down(self):
        Base.metadata.drop_all(self.engine)

    def test_procedimento(self):
        self.set_up()
        procedimento = Procedimento('teste')
        assert procedimento.nome == 'teste'
        self.session.commit()
        # assert procedimento.id is not None
        self.tear_down()

    def test_site(self):
        self.set_up()
        site = Site('teste', 'url')
        assert site.title == 'teste'
        assert site.url == 'url'
        self.session.commit()
        self.tear_down()
        # assert site.id is not None

    def test_produto(self):
        self.set_up()
        produto = Produto('teste', 1.99)
        assert produto.descricao == 'teste'
        self.session.commit()
        # assert produto.id is not None
        self.tear_down()

    def test_vincula_produto(self):
        self.set_up()
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
        self.tear_down()

    def test_dossie(self):
        self.set_up()
        procedimento = Procedimento('teste')
        data = date(2017, 10, 31)
        dossie = Dossie(procedimento, data)
        self.session.commit()
        assert dossie.procedimento_id == procedimento.id
        assert dossie.data == data
        self.tear_down()

    def test_produtoencontrado(self):
        self.set_up()
        procedimento = Procedimento('teste')
        dossie = Dossie(procedimento, '2017-10-31')
        produto = Produto('teste', 1.99)
        site = Site('teste', 'url')
        produtoencontrado = ProdutoEncontrado(
            dossie, produto, site, 'teste', 'www.teste', 1.00)
        self.session.commit()
        assert produtoencontrado.dossie_id == dossie.id
        assert produtoencontrado.descricao_site == 'teste'
        assert produtoencontrado.url == 'www.teste'
        assert produtoencontrado.preco == 1.00
