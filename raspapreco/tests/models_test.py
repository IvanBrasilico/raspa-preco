import unittest

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from raspapreco.models.models import Procedimento, Produto, Site


class TestModel(unittest.TestCase):
    def set_up(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.Base = declarative_base()
        self.Base.metadata.create_all(self.engine)

    def tear_down(self):
        self.Base.metadata.drop_all(self.engine)

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

    def test_open_site(self):

    def test_produto(self):
        self.set_up()
        produto = Produto('teste')
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
        produto = Produto('teste')
        assert produto.descricao == 'teste'
        produto.id = 1  # Memory does not have autoincrement
        produto2 = Produto('teste2')
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
