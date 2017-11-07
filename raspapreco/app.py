from flask import Flask, Response, redirect, url_for, request, session, abort
from flask_login import current_user, LoginManager, UserMixin, \
    login_required, login_user, logout_user
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

from raspapreco.restless import app

# config
app.config.update(
    SECRET_KEY='secret_xxx'
)


class User(UserMixin):
        # proxy for a database of users
    user_database = {"ivan": ("ivan", "ivan1234")}

    def __init__(self, username, password):
        self.id = username
        self.name = username
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)


def authenticate(username, password):
    print(username, password)
    user_entry = User.get(username)
    print(user_entry)
    if user_entry is not None:
        user = User(user_entry[0], user_entry[1])
        print(user)
        if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
            return user


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


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# somewhere to login


@app.route("/api/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return current_user.name

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_entry = User.get(username)
        if user_entry is not None:
            user = User(user_entry[0], user_entry[1])
            if user.password == password:
                login_user(user)
                return redirect('/')
        return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    user_entry = User.get(userid)
    user = User(user_entry[0], user_entry[1])
    return user


if __name__ == "__main__":
    app.run()
