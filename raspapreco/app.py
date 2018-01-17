from flask import Flask, Response, abort, redirect, request, session, url_for
from flask_jwt import JWT, current_identity, jwt_required
from werkzeug.security import safe_str_cmp

from raspapreco.restless import app


class User():
    # proxy for a database of users
    user_database = {'ivan': ('ivan', 'ivan')}

    def __init__(self, username, password):
        self.id = username
        self.name = username
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)


def authenticate(username, password):
    user_entry = User.get(username)
    if user_entry is not None:
        user = User(user_entry[0], user_entry[1])
        if user and safe_str_cmp(user.password.encode('utf-8'),
                                 password.encode('utf-8')):
            return user
    return None


def identity(payload):
    user = ''
    user_id = payload['identity']
    user_entry = User.get(user_id)
    if user_entry is not None:
        user = User(user_entry[0], user_entry[1])
    return user


jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


if __name__ == '__main__':
    app.run()
