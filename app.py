from datetime import datetime

import flask
from flask import Flask
from database.database import db, init_database
from database.models import Group, User, Message, group_user_table
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

#makes an user join a group
def join_group(user, group):
    group.users.append(user)
    db.session.add(user)
    db.session.commit()
    return

#checks if an user is in a group
def is_in_group(user_id, group_id):
    return db.session.query(group_user_table).filter_by(group_id=group_id, user_id=user_id).first() is not None

@app.route('/')
@app.route('/messages')
def messages():
    groups = Group.query.all()
    return flask.render_template("messages.html.jinja2", groups=groups)

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

@app.route('/send', methods=['POST','GET'])
def form_send_msg():
    form_is_valid, errors = is_form_valid(flask.request.form)
    if not form_is_valid:
        return show_form(flask.request.form, errors)
    else:
        return send_form(flask.request.form)
    return flask.render_template('messages.html.jinja2')

#form is invalid if: user or group doesn't exist, user is not in group, msg is empty
def is_form_valid(form):
    result = True
    errors = []

    user_id = form.get('user_id', "")
    if user_id == "":
        result = False
        errors += ['user field is empty']
    else:
        user = User.query.filter_by(id=user_id).first()
        if user == "":
            result = False
            errors += ['user does not exist']

    group_id = form.get('group_id', "")
    if user_id == "":
        result = False
        errors += ['group field is empty']
    else:
        group = Group.query.filter_by(id=group_id).first()
        if group == "":
            result = False
            errors += ['group does not exist']

    content = form.get('msg', "")
    if content == "":
        result = False
        errors += ['msg field is empty']

    if result and not is_in_group(user_id, group_id):
        result = False
        errors += ['user in not in group']

    print("############", errors)
    return result, errors

def show_form(form, errors):
    return flask.render_template('send.html.jinja2', errors = errors)

def send_form(form):
    user = User.query.filter_by(id=form.get('user_id')).one()
    group = Group.query.filter_by(id=form.get('group_id')).one()
    msg = create_message(
        content=form.get('msg'),
        user=user,
        group=group
    )
    return flask.render_template('send.html.jinja2')



if __name__ == '__main__':
    app.run()
