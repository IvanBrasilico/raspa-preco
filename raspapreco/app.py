from flask import Flask, Response, redirect, url_for, request, session, abort
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

from raspapreco.restless import app

app.config.update(SECRET_KEY='secret_xxx',
                  JWT_AUTH_URL_RULE='/api/auth')


class User():
    # proxy for a database of users
    user_database = {'ivan': ('ivan', 'ivan1234')}

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
    user_id = payload['identity']
    user_entry = User.get(user_id)
    if user_entry is not None:
        user = User(user_entry[0], user_entry[1])
    return user


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


jwt = JWT(app, authenticate, identity)

if __name__ == '__main__':
    app.run()
