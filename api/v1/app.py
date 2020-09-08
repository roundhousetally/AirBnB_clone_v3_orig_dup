#!/usr/bin/python3
""" api """
from flask import Flask
from os import getenv
from models import storage
from api.v1.views import app_views
app = Flask(__name__)
app.register_blueprint(app_views, url_prefix="/api/v1")


@app.teardown_appcontext
def tear_down(self):
    """ calls close """
    storage.close()


@app.errorhandler(404)
def fourohfour(self):
    """Returns a 404 error with JSON response"""
    return {"error": "Not found"}, 404


if __name__ == "__main__":
    app.run(host=getenv("HBNB_API_HOST"), port=getenv("HBNB_API_PORT"),
            threaded=True, debug=True)