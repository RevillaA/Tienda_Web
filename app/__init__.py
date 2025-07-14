# app/__init__.py
from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ⚠️ Clave insegura para pruebas de seguridad (NO usar en producción)
    app.secret_key = "clave-insegura"

    mysql.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app
