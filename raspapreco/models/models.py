import os

from sqlalchemy import (Column, ForeignKey, Integer, String, Table,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

path = os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:////' + path +
                       '/raspa.db', convert_unicode=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = scoped_session(Session)
Base.metadata.bind = engine

produto_procedimento = Table('produto_procedimento', Base.metadata,
                             Column('left_id', Integer,
                                    ForeignKey('procedimentos.id')),
                             Column('right_id', Integer,
                                    ForeignKey('produtos.id'))
                             )

site_procedimento = Table('site_procedimento', Base.metadata,
                          Column('left_id', Integer,
                                 ForeignKey('procedimentos.id')),
                          Column('right_id', Integer,
                                 ForeignKey('sites.id'))
                          )


class Procedimento(Base):
    """Guarda os dados do procedimento"""
    __tablename__ = 'procedimentos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(20), unique=True)
    produtos = relationship(
        'Produto',
        secondary=produto_procedimento,
        back_populates='procedimentos')
    sites = relationship(
        'Site',
        secondary=site_procedimento,
        back_populates='procedimentos')

    def __init__(self, nome):
        self.nome = nome


class Produto(Base):
    """Um produto a pesquisar"""
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    descricao = Column(String(50), unique=True)
    procedimentos = relationship(
        'Procedimento',
        secondary=produto_procedimento,
        back_populates='produtos')

    def __init__(self, descricao):
        self.descricao = descricao


class Site(Base):
    """Um site que será fonte de dados"""
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    title = Column(String(20), unique=True)
    url = Column(String(200))
    procedimentos = relationship(
        'Procedimento',
        secondary=site_procedimento,
        back_populates='sites')

    def __init__(self, title, url):
        self.title = title
        self.url = url


if __name__ == '__main__':
    Base.metadata.create_all(engine)
