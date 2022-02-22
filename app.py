from datetime import datetime

import flask
from flask import Flask
from database.database import db, init_database
from database.models import Group, User, Message
import flask


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

with app.test_request_context():
    init_database()

#cleaning all db
@app.route('/clean')
def db_clean():
    db.drop_all()
    db.create_all()
    return "Cleaned!"

def create_user(name):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return user

def create_group(name):
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()
    return group

def create_message(content, user, group):
    msg = Message(content=content, sender=user, group=group, date=datetime.now())
    db.session.add(msg)
    db.session.commit()
    return msg

def join_group(user, group):
    group.users.append(user)
    db.session.add(user)
    db.session.commit()
    return

@app.route('/login')
def login():  # put application's code here
    return flask.render_template("login.html.jinja2")

@app.route('/test')
def test():
    user1 = create_user('Robin')
    group1 = create_group('Equipe 1')
    join_group(user1, group1)
    create_message('uwu', user1, group1)

    groups = Group.query.all()

    return flask.render_template('test.html.jinja2', groups=groups)

if __name__ == '__main__':
    app.run()
