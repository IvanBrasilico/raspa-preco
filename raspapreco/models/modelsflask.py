import os

import flask
import flask.ext.sqlalchemy

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
path = os.path.dirname(os.path.abspath(__file__))
db_file = 'sqlite:////' + path + '/raspaflask.db'
print(db_file)
app.config['SQLALCHEMY_DATABASE_URI'] = db_file
db = flask.ext.sqlalchemy.SQLAlchemy(app)


produto_procedimento = db.Table('produto_procedimento',
                                db.Column('produto_id', db.Integer,
                                          db.ForeignKey('produto.id'),
                                          primary_key=True),
                                db.Column('procedimento_id', db.Integer,
                                          db.ForeignKey('procedimento.id'),
                                          primary_key=True)
                                )

site_procedimento = db.Table('site_procedimento',
                             db.Column('site_id', db.Integer,
                                       db.ForeignKey('site.id'),
                                       primary_key=True),
                             db.Column('procedimento_id', db.Integer,
                                       db.ForeignKey('procedimento.id'),
                                       primary_key=True)
                             )


class Procedimento(db.Model):
    """Guarda os dados do procedimento"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True)
    produtos = db.relationship(
        "Produto",
        secondary=produto_procedimento,
        backref=db.backref('procedimentos'))
    sites = db.relationship(
        "Site",
        secondary=site_procedimento,
        backref=db.backref('procedimentos'))

    def __init__(self, nome):
        self.nome = nome


class Produto(db.Model):
    """Um produto a pesquisar"""
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), unique=True)

    def __init__(self, descricao):
        self.descricao = descricao


class Site(db.Model):
    """Um site que será fonte de dados"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    url = db.Column(db.String(200))

    def __init__(self, title, url):
        self.title = title
        self.url = url
