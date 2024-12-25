from app import db
from flask_login import UserMixin
from sqlalchemy import func,ForeignKey
from datetime import datetime
class Login(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('login.id'))
    
    def __repr__(self):
        return f"<Admin {self.name}>"

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    fullname = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id', ondelete="CASCADE"))
    experience = db.Column(db.Integer, nullable=False) 
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    ratings = db.Column(db.Integer, nullable=True) #Ratings column added for Professional Model
    remarks = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=None, nullable=True)
    login_id = db.Column(db.Integer, db.ForeignKey('login.id', ondelete="CASCADE"))
    service_requests = db.relationship('ServiceRequest', backref='professional', passive_deletes=True)
    
    def __repr__(self):
        
        return f"<Sponsor {self.name}>"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('login.id', ondelete="CASCADE"))
    service_requests = db.relationship('ServiceRequest', backref='customer', passive_deletes=True)

    def __repr__(self):
        return f"<Influencer {self.name}>"

class Service(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)  
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('open', 'close', name='service_status'), default='open', nullable=False)

    service_requests = db.relationship('ServiceRequest', backref='service', passive_deletes=True)


    def __repr__(self):
        return f'<Service {self.service_name}>'

class ServiceRequest(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, ForeignKey('service.id', ondelete="CASCADE"), nullable=False ) 
    customer_id = db.Column(db.Integer, ForeignKey('customer.id', ondelete="CASCADE"), nullable=False)
    professional_id = db.Column(db.Integer, ForeignKey('professional.id', ondelete="CASCADE"), nullable=False)
    date_of_request = db.Column(db.DateTime(timezone=True), default=datetime.now, nullable=False)
    date_of_completion = db.Column(db.DateTime(timezone=True), nullable=True)
    service_status = db.Column(db.String(100), default='Requested', nullable=False)
