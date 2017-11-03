import sys
import time

import flask_restless
from flask import Flask, jsonify, url_for, redirect
from flask_cors import CORS
from celery import Celery

from raspapreco.models.models import (Base, MySession, Procedimento, Produto,
                                      Site)
from raspapreco.utils.dossie_manager import DossieManager
from raspapreco.utils.site_scraper import scrap_one

mysession = MySession(Base)
session = mysession.session()

app = Flask(__name__)

celery = Celery(app.name, broker='pyamqp://guest@localhost//',
                backend='rpc://')


@celery.task(bind=True)
def raspac(self, procedimento):
    """Background task that runs a long function with progress reports.
    https://blog.miguelgrinberg.com/post/using-celery-with-flask
    """
    proc = session.query(Procedimento).filter(
        Procedimento.id == procedimento).first()
    total = len(proc.produtos) * len(proc.sites)
    cont = 0
    self.update_state(state='PROGRESS',
                      meta={'current': cont, 'total': total,
                            'status': 'Raspando Sites...'})
    scraped = {}
    for produto in proc.produtos:
        produtos_scrapy = {}
        for site in proc.sites:
            self.update_state(state='PROGRESS',
                              meta={'current': cont, 'total': total,
                                    'status': 'Raspando Sites...'})
            produtos_scrapy[site.id] = scrap_one(site, produto)
            cont += 1
        scraped[produto.id] = produtos_scrapy
        time.sleep(0.2)  # Prevent site blocking

    dossiemanager = DossieManager(session, proc)
    dossiemanager.monta_dossie(scraped)
    self.update_state(state='PROGRESS',
                      meta={'current': 100, 'total': 100,
                            'status': 'Quase',
                            'result': dossiemanager.dossie_to_html_table()})
    return {'current': 100, 'total': 100,
            'status': 'Finalizado',
            'result': dossiemanager.dossie_to_html_table()}


if len(sys.argv) > 1:
    if sys.argv[1] == '--debug':
        app.config['DEBUG'] = True
        app.config['static_url_path'] = '/static'

        @app.route('/')
        def hello_world():
            with open('raspapreco/site/index.html') as f:
                home = f.read()
            return home

        @app.route('/api/dossie')
        def dossie():
            with open('raspapreco/site/dossie.html') as f:
                fdossie = f.read()
            return fdossie

        @app.route('/api/scrap/<procedimento>')
        def scrap(procedimento):
            proc = session.query(Procedimento).filter(
                Procedimento.id == procedimento).first()
            executor = DossieManager(session, proc)
            executor.raspa()
            return executor.dossie_to_html_table()


@app.route('/api/scrapc/<procedimento>')
def scrapc(procedimento):
    task = raspac.delay(procedimento)
    if app.config['DEBUG'] is True:
        return redirect(url_for('dossie') + '?task_id=' + task.id)
    else:
        return redirect('/raspapreco/dossie.html?task_id=' + task.id)


@app.route('/api/scrapprogress/<task_id>')
def scrapprogress(task_id):
    task = raspac.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pendente...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


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
