from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_database():
    db.create_all()