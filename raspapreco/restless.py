import flask_restless
from flask_cors import CORS

# from models.modelsflask import app, db, Procedimento, Site
from raspapreco.models.models import Procedimento, Produto, Site, app, session

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, session=session)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Produto, methods=['GET', 'POST', 'DELETE', 'PUT'])
manager.create_api(Procedimento, methods=['GET', 'POST', 'PUT'])
manager.create_api(Site, methods=['GET', 'POST', 'PUT', 'DELETE'])

# start the flask loop
CORS(app)
if __name__ == '__main__':
    app.run()
