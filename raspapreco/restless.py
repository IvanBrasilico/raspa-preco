import sys

import flask_restless
from flask import Flask, jsonify
from flask_cors import CORS

from raspapreco.models.models import Procedimento, Produto, Site, session
from raspapreco.utils.site_scraper import Scraper

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
            proc = session.query(Procedimento).filter(Procedimento.id == procedimento).first()
            scrap = Scraper(proc.sites, proc.produtos)
            scrap.scrap()
            return jsonify(scrap.scraped)

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
