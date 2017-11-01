"""Tests and documents use of the API
Any client must make this type of request to API
Made from Flask_restless API docs and Flask testing docs
http://flask.pocoo.org/docs/0.12/testing/
https://flask-restless.readthedocs.io/en/stable/requestformat.html
"""
import json
import unittest
from urllib.parse import urlencode

import raspapreco.restless as restless


class FlaskTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.siteid = 0
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        restless.app.testing = True
        self.app = restless.app.test_client()

    def tearDown(self):
        pass

    def test_not_found(self):
        rv = self.app.get('/')
        assert b'404 Not Found' in rv.data

    def test_api(self):
        siteid = self._post()
        title = self._get(siteid)
        self._query(title)
        self._put(siteid)
        self._delete(siteid)

    def _post(self):
        rv = self.app.post('/api/sites', data=json.dumps({'title': 'test',
                                                          'url': 'url'}),
                           follow_redirects=True,
                           headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"title": "test"' in rv.data
        assert b'"url": "url"' in rv.data
        return fields['id']

    def _get(self, siteid):
        rv = self.app.get('/api/sites/' + str(siteid), follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert siteid == fields['id']
        assert fields['title'] == 'test'
        assert fields['url'] == 'url'
        return fields['title']

    def _query(self, title):
        headers = {'Content-Type': 'application/json'}
        filters = [dict(name='title', op='like', val='%' + title + '%')]
        params = dict(q=json.dumps(dict(filters=filters)))
        params = urlencode(params)
        url = '/api/sites?%s' % params
        rv = self.app.get(url,
                          headers=headers)
        print(rv.data)
        fields = json.loads(rv.data.decode('utf-8'))
        assert fields['objects'][0]['title'].lower().find(title.lower()) != -1

    def _put(self, siteid):
        rv = self.app.put('/api/sites/' + str(siteid),
                          data=json.dumps({'title': 'test2',
                                           'url': 'url2'}),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"title": "test2"' in rv.data
        assert b'"url": "url2"' in rv.data
        return fields['id']

    def _delete(self, siteid):
        rv = self.app.delete('/api/sites/' + str(siteid),
                             follow_redirects=True,
                             headers={'Content-Type': 'application/json'})
        print(rv.data)
        # fields = json.loads(rv.data.decode("utf-8"))
        assert rv.data == b''

    def test_apiproduto(self):
        produtoid = self._postproduto()
        descricao = self._getproduto(produtoid)
        self._queryproduto(descricao)
        self._putproduto(produtoid)
        self._deleteproduto(produtoid)

    def _postproduto(self):
        rv = self.app.post('/api/produtos',
                           data=json.dumps({'descricao': 'test'}),
                           follow_redirects=True,
                           headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"descricao": "test"' in rv.data
        return fields['id']

    def _getproduto(self, produtoid):
        rv = self.app.get('/api/produtos/' + str(produtoid),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert produtoid == fields['id']
        assert fields['descricao'] == 'test'
        return fields['descricao']

    def _queryproduto(self, descricao):
        headers = {'Content-Type': 'application/json'}
        filters = [dict(name='descricao', op='like',
                        val='%' + descricao + '%')]
        params = dict(q=json.dumps(dict(filters=filters)))
        params = urlencode(params)
        url = '/api/produtos?%s' % params
        rv = self.app.get(url,
                          headers=headers)
        print(rv.data)
        fields = json.loads(rv.data.decode('utf-8'))
        assert fields['objects'][0]['descricao'].find(descricao) != -1

    def _putproduto(self, id):
        rv = self.app.put('/api/produtos/' + str(id),
                          data=json.dumps({'descricao': 'test2'}),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"descricao": "test2"' in rv.data
        return fields['id']

    def _deleteproduto(self, produtoid):
        rv = self.app.delete('/api/produtos/' + str(produtoid),
                             follow_redirects=True,
                             headers={'Content-Type': 'application/json'})
        print(rv.data)
        # fields = json.loads(rv.data.decode("utf-8"))
        assert rv.data == b''

    def test_apiprocedimento(self):
        id = self._postprocedimento()
        campo = self._getprocedimento(id)
        self._queryprocedimento(campo)
        self._putprocedimento(id)
        siteid = self._post()
        produtoid = self._postproduto()
        self._putprocedimentosite(id, siteid)
        self._putprocedimentoproduto(id, produtoid)
        self._delete(siteid)
        self._deleteproduto(produtoid)
        self._deleteprocedimento(id)

    def _postprocedimento(self):
        rv = self.app.post('/api/procedimentos',
                           data=json.dumps({'nome': 'test'}),
                           follow_redirects=True,
                           headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"nome": "test"' in rv.data
        return fields['id']

    def _getprocedimento(self, id):
        rv = self.app.get('/api/procedimentos/' + str(id),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert id == fields['id']
        assert fields['nome'] == 'test'
        return fields['nome']

    def _queryprocedimento(self, campo):
        headers = {'Content-Type': 'application/json'}
        filters = [dict(name='nome', op='like', val='%' + campo + '%')]
        params = dict(q=json.dumps(dict(filters=filters)))
        params = urlencode(params)
        url = '/api/procedimentos?%s' % params
        rv = self.app.get(url,
                          headers=headers)
        print(rv.data)
        fields = json.loads(rv.data.decode('utf-8'))
        assert fields['objects'][0]['nome'].lower().find(campo.lower()) != -1

    def _putprocedimento(self, id):
        rv = self.app.put('/api/procedimentos/' + str(id),
                          data=json.dumps({'nome': 'test2'}),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"nome": "test2"' in rv.data
        return fields['id']

    def _putprocedimentosite(self, id, siteid):
        rv = self.app.put('/api/procedimentos/' + str(id),
                          data=json.dumps({'sites':
                                           {'add': [{'id': siteid}]}
                                           }),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        # assert b'"nome": "test2"' in rv.data
        return fields['id']

    def _putprocedimentoproduto(self, id, produtoid):
        rv = self.app.put('/api/procedimentos/' + str(id),
                          data=json.dumps({'produtos':
                                           {'add': [{'id': produtoid}]}
                                           }),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        # assert b'"nome": "test2"' in rv.data
        return fields['id']

    def _deleteprocedimento(self, id):
        rv = self.app.delete('/api/procedimentos/' + str(id),
                             follow_redirects=True,
                             headers={'Content-Type': 'application/json'})
        print(rv.data)
        # fields = json.loads(rv.data.decode("utf-8"))
        assert rv.data == b''


if __name__ == '__main__':
    unittest.main()
