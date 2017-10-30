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
                          headers={'Content-Type': 'application/json'})
        print(rv.data)
        fields = json.loads(rv.data.decode('utf-8'))
        assert fields['objects'][0]['title'].find(title) != -1

    def _put(self, siteid):
        rv = self.app.put('/api/sites/' + str(siteid), data=json.dumps({'title': 'test2',
                                                                        'url': 'url2'}),
                          follow_redirects=True,
                          headers={'Content-Type': 'application/json'})
        fields = json.loads(rv.data.decode('utf-8'))
        assert b'"title": "test2"' in rv.data
        assert b'"url": "url2"' in rv.data
        return fields['id']

    def _delete(self, siteid):
        rv = self.app.delete('/api/sites/' + str(siteid), follow_redirects=True,
                             headers={'Content-Type': 'application/json'})
        print(rv.data)
        # fields = json.loads(rv.data.decode("utf-8"))
        assert rv.data == b''


if __name__ == '__main__':
    unittest.main()
