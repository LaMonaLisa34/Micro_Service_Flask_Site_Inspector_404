# app/__init__.py
from flask import Flask
from .routes import bp as routes_bp
from .models import init_db

def create_app():
    app = Flask(__name__)

    # init DB une seule fois au démarrage de l’app
    with app.app_context():
        init_db()

    app.register_blueprint(routes_bp)
    return app
