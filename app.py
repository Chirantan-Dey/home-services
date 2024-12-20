from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()

def create_app():
    app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')
    app.config['SECRET_KEY'] = '8f42a73054b1749f8f58848be5e6502c'    

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    
     
    
    db.init_app(app)
    
    from routes import routes
    app.register_blueprint(routes, url_prefix="/")

    from models import Login,Admin,Professional,Customer,Service,ServiceRequest
    
    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Login.query.get(id)

        
    from routes import register_routes
    register_routes(app,db)

    
    return app