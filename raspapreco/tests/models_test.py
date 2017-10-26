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
        # assert site.id is not None
        self.tear_down()

    def test_produto(self):
        self.set_up()
        produto = Produto('teste')
        assert produto.descricao == 'teste'
        self.session.commit()
        # assert produto.id is not None
        self.tear_down()
        



