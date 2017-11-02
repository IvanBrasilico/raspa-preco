import sys

import flask_restless
from flask import Flask, jsonify
from flask_cors import CORS

from raspapreco.models.models import (Base, MySession, Procedimento, Produto,
                                      Site)
from raspapreco.utils.dossie_manager import DossieManager

mysession = MySession(Base)
session = mysession.session()

app = Flask(__name__)

if len(sys.argv) > 1:
    if sys.argv[1] == '--debug':
        app.config['DEBUG'] = True
        app.config['static_url_path'] = '/static'

        @app.route('/')
        def hello_world():
            with open('raspapreco/site/index.html') as f:
                home = f.read()
            return home

        @app.route('/api/scrap/<procedimento>')
        def scrap(procedimento):
            proc = session.query(Procedimento).filter(
                Procedimento.id == procedimento).first()
            executor = DossieManager(session, proc)
            executor.scrap()
            return executor.dossie_to_html_table()

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, session=session)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Produto, methods=['GET', 'POST', 'DELETE', 'PUT'])
manager.create_api(Procedimento, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(Site, methods=['GET', 'POST', 'PUT', 'DELETE'])

# start the flask loop
CORS(app)
if __name__ == '__main__':
    app.run()
