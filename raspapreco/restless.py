import sys
import time
from datetime import datetime

import flask_restless
from celery import Celery
from flask import Flask, Response, jsonify, redirect, url_for
from flask_cors import CORS
from flask_jwt import JWT, jwt_required
from json_tricks import dumps

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, Site)
from raspapreco.utils.dossie_manager import DossieManager
from raspapreco.utils.site_scraper import scrap_one

mysession = MySession(Base)
session = mysession.session()

app = Flask(__name__)
CORS(app)
app.config.update(SECRET_KEY='secret_xxx',
                  JWT_AUTH_URL_RULE='/api/auth')


celery = Celery(app.name, broker='pyamqp://guest@localhost//',
                backend='rpc://')


@celery.task(bind=True)
def raspac(self, dossie_id):
    """Background task that runs a long function with progress reports.
    https://blog.miguelgrinberg.com/post/using-celery-with-flask
    """
    dossie = session.query(Dossie).filter(
        Dossie.id == dossie_id).first()
    proc = dossie.procedimento
    total = len(proc.produtos) * len(proc.sites)
    cont = 0
    dossiemanager = DossieManager(session, proc, dossie)
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
    dossiemanager.raspa(scraped)
    dossie.task_id = ''
    session.merge(dossie)
    session.commit()
    return {'current': 100, 'total': 100,
            'status': 'Finalizado',
            'result': {'id': dossie.id, 'data': dossie.data}}


if len(sys.argv) > 1:
    if sys.argv[1] == '--debug':
        app.config['DEBUG'] = True
        app.config['static_url_path'] = '/static'

        @app.route('/')
        def hello_world():
            with open('raspapreco/site/index.html') as f:
                home = f.read()
            return home

        @app.route('/api/dossie_home')
        def dossie_home():
            with open('raspapreco/site/dossie.html') as f:
                fdossie = f.read()
            return fdossie

        @app.route('/api/scrap/<procedimento>')
        def scrap(procedimento):
            proc = session.query(Procedimento).filter(
                Procedimento.id == procedimento).first()
            executor = DossieManager(session, proc)
            executor.raspa()
            return redirect(url_for('dossie_home') + '?procedimento_id=' +
                            str(proc.id))


@app.route('/api/login_form')
def login_form():
    with open('raspapreco/site/login.html') as f:
        flogin = f.read()
    return flogin


if app.config['DEBUG'] is False:
    @app.route('/api/scrap/<procedimento>')
    def scrapc(procedimento):
        proc = session.query(Procedimento).filter(
            Procedimento.id == procedimento).first()
        dossiemanager = DossieManager(session, proc)
        task = raspac.delay(procedimento)
        dossie = dossiemanager.inicia_dossie(task.id)
        session.merge(dossie)
        session.commit()
        return redirect('/raspapreco/dossie.html?procedimento_id=' +
                        str(proc.id))


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


@app.route('/api/dossietable/<dossie_id>')
def dossie_table(dossie_id):
    dossie = session.query(Dossie).filter(
        Dossie.id == dossie_id).first()
    dossiemanager = DossieManager(session, dossie=dossie)
    return dumps(dossiemanager.dossie_to_html_table())


@app.route('/api/procedimentos/delete_children/<procedimento>')
def delete_children(procedimento):
    proc = session.query(Procedimento).filter(
        Procedimento.id == procedimento).first()
    proc.sites = []
    proc.produtos = []
    session.merge(proc)
    session.commit()
    return jsonify({'message': 'procedimento atualizado'}), 200


# Create the Flask-Restless API manager.
@jwt_required()
def auth_func(**kw):
    pass


if 'pytest' in sys.modules:
    manager = flask_restless.APIManager(app, session=session)
else:
    manager = flask_restless.APIManager(app, session=session,
                                        preprocessors=dict(POST=[auth_func],
                                                           GET=[auth_func],
                                                           GET_MANY=[
                                                               auth_func],
                                                           PUT=[auth_func],
                                                           DELETE=[auth_func]))

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Produto, methods=['GET', 'POST', 'DELETE', 'PUT'])
manager.create_api(Procedimento, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(Site, methods=['GET', 'POST', 'PUT', 'DELETE'])

# start the flask loop
if __name__ == '__main__':
    app.run()
