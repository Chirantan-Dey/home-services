# from flask import *
# from flask_sqlalchemy import *
# from os import *
# from flask_login import *

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')
    app.config['SECRET_KEY'] = '8f42a73054b1749f8f58848be5e6502c'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)
    
    from .routes import routes_bp
    app.register_blueprint(routes_bp, url_prefix="/")

    from .models import Login,Admin,Professional,Customer,Service,ServiceRequest
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'routes_bp.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Login.query.get(id)

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created database!")