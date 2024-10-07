from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .app import app
from flask_migrate import Migrate



 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Loginto12@localhost/control'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Declared(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    declaration_number = db.Column(db.String(50), nullable=False)  # Make declaration_number unique
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    amount_unit = db.Column(db.String(20), nullable=True)
    measurement = db.Column(db.Float, nullable=False)
    measurement_unit = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)

    balances = db.relationship('Balance', backref='declared', lazy=True)


class Imported(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    declaration_number = db.Column(db.String(50), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    amount_unit = db.Column(db.String(20), nullable=True)
    measurement = db.Column(db.Float, nullable=False)
    measurement_unit = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)

class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
   # declaration_number = db.Column(db.String(50), nullable=False)  # Make declaration_number unique
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    declaration_number = db.Column(db.String(100), db.ForeignKey('declared.declaration_number'), nullable=False)
   



# Create the database tables
with app.app_context():
    db.create_all()