import unittest

import raspapreco.app as app


class TestApp(unittest.TestCase):
    def setUp(self):
        app.app.testing = True

    def test_login(self):
        aut = app.authenticate('ivan', 'ivan')
        assert aut is not None
        id = {'identity': 1}
        app.identity(id)
