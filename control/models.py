from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin 
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from control.extensions import db



 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Loginto12@localhost/control'


class Declared(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    declaration_number = db.Column(db.String(50), unique=True, nullable=False)  # Unique constraint added
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    amount_unit = db.Column(db.String(20), nullable=True)
    measurement = db.Column(db.Float, nullable=False)
    measurement_unit = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)

    
class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    declaration_number = db.Column(db.String(50), nullable=False,index=True)
    


class Imported(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    declaration_number = db.Column(db.String(50), nullable=False, index=True)
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    amount_unit = db.Column(db.String(20), nullable=True)
    measurement = db.Column(db.Float, nullable=False)
    measurement_unit = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)

class Ticket(db.Model):
    __tablename__ = 'tickets'  # Specify the table name if needed

    id = db.Column(db.Integer, primary_key=True)
    ticket_no = db.Column(db.String(50), nullable=False)
    plate_no = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Foreign key relationship
    declaration_number = db.Column(db.String(50), db.ForeignKey('imported.declaration_number'), nullable=False)

    # Backref to Imported model
    imported = db.relationship('Imported', backref='tickets')

    def __repr__(self):
        return f'<Ticket {self.ticket_no}>'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)  # Middle name can be optional
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)


    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

# Action/Log model
class LoginAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('actions', lazy=True)) 