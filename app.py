from flask import Flask
from routes import pages


def create_app():
    app = Flask(__name__)
    app.secret_key = "ZmbwC_HVm0WjhTqx6ZsKUkDafWIjQYU_t0JFxx0AJH4"
    app.config["SESSION_TYPE"] = 'mongodb'
    app.register_blueprint(pages)

    return app
