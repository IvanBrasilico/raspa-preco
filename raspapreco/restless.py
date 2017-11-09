import os
import sys
import time

import flask_restless
import jinja2
from celery import Celery
from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, url_for)
from flask_cors import CORS
from flask_jwt import jwt_required
from json_tricks import dumps

from raspapreco.models.models import (Base, Dossie, MySession, Procedimento,
                                      Produto, Site)
from raspapreco.utils.dossie_manager import DossieManager
from raspapreco.utils.site_scraper import scrap_one

mysession = MySession(Base)
session = mysession.session()

app = Flask(__name__)
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('raspapreco/site'),
])
app.jinja_loader = my_loader
CORS(app)
app.config.update(SECRET_KEY='secret_xxx',
                  JWT_AUTH_URL_RULE='/api/auth')


celery = Celery(app.name, broker='pyamqp://guest@localhost//',
                backend='rpc://')


@celery.task(bind=True)
def raspac(self, dossie_id, refazer=False):
    """Background task that runs a long function with progress reports.
    https://blog.miguelgrinberg.com/post/using-celery-with-flask
    """
    dossie = session.query(Dossie).filter(
        Dossie.id == dossie_id).first()
    proc = dossie.procedimento
    total = len(proc.produtos) * len(proc.sites)
    cont = 0
    self.update_state(state='PROGRESS',
                      meta={'current': cont, 'total': total,
                            'status': 'Raspando Sites...'})
    # Já houve scrap anterior? Se houve, somente refaz se
    # expressamente comandado
    if refazer or (not dossie.produtos_encontrados):
        # TODO: Tentar transformar linhas abaixo em um generator
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
        dossiemanager = DossieManager(session, proc, dossie)
        dossiemanager.scraped = scraped
        dossiemanager.monta_dossie()
        dossie.task_id = ''
        session.merge(dossie)
        session.commit()
    # FIM linhas
    return {'current': 100, 'total': 100,
            'status': 'Finalizado',
            'result': {'id': dossie.id, 'data': dossie.data}}


if len(sys.argv) > 1:
    if sys.argv[1] == '--debug':
        app.config['DEBUG'] = True


if os.environ.get('DEBUG', 'None') == '1':
    app.config['DEBUG'] = True

if app.config['DEBUG']:
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

    @jwt_required()
    @app.route('/api/scrap')
    def scrap():
        procedimento = request.args.get('procedimento')
        refazer = request.args.get('refazer')
        proc = session.query(Procedimento).filter(
            Procedimento.id == procedimento).first()
        manager = DossieManager(session, proc)
        manager.raspa(refazer == '1')
        return redirect(url_for('dossie_home') + '?procedimento_id=' +
                        str(proc.id))


@app.route('/api/login_form')
def login_form():
    return render_template('login.html')


if app.config['DEBUG'] is False:
    @jwt_required()
    @app.route('/api/scrap')
    def scrapc():
        procedimento = request.args.get('procedimento')
        refazer = request.args.get('refazer')
        proc = session.query(Procedimento).filter(
            Procedimento.id == procedimento).first()
        dossiemanager = DossieManager(session, proc)
        refaz = refazer == '1'
        dossie = dossiemanager.inicia_dossie(refaz)
        task = raspac.delay(dossie.id, refaz)
        dossie.task_id = task.id
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


@jwt_required()
@app.route('/api/procedimentos/delete_children/<procedimento>')
def delete_children(procedimento):
    proc = session.query(Procedimento).filter(
        Procedimento.id == procedimento).first()
    proc.sites.clear()
    proc.produtos.clear()
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
