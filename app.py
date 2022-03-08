from datetime import datetime

import flask
from flask import redirect, url_for
from flask_login import login_required, LoginManager, login_user, current_user
from database.database import db, init_database
from database.models import Group, User, Message, group_user_table

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'xxxxyyyyyzzzzz'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'logintest'

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

@login_required
@app.route('/t/<group_id>', methods=['POST','GET'])
def messages(group_id):
    groups = Group.query.all()
    active_group = Group.query.filter_by(id=group_id).one()

    form = flask.request.form
    msg_form_is_valid, errors = is_msg_form_valid(form)
    if msg_form_is_valid:
        #POST method
        create_message(
            content=form.get('msg'),
            user=current_user,
            group=active_group)
    #GET method
    return flask.render_template("messages.html.jinja2",
                                 groups=groups,  active_group=active_group, errors = errors)


@app.route('/login', methods=['POST','GET'])
def login():
    #GET requests display the login form
    #POST methods process the login form
    form = flask.request.form
    form_is_valid, errors = is_login_form_valid(form)

    if form_is_valid:
        user = User.query.filter_by(id=form.get('user_id')).first()
        user.authenticated = True
        login_user(user)
        return redirect(url_for("messages", group_id=1))

    return flask.render_template("logintest.html.jinja2", form=form, errors=errors)

@app.route('/debug/users', methods=['POST','GET'])
def debug_users():

    form = flask.request.form
    create_user(
        name=form.get('user_name')
    )
    users = User.query.all()
    return flask.render_template('debug/users.html.jinja2', users=users)

@app.route('/debug/groups', methods=['POST','GET'])
def debug_groups():

    form = flask.request.form
    create_group(
        name=form.get('group_name')
    )
    groups = Group.query.all()
    return flask.render_template('debug/groups.html.jinja2', groups=groups)

@app.route('/debug/participations', methods=['POST','GET'])
def debug_participations():

    form = flask.request.form
    form_is_valid, errors = is_debug_part_form_valid(form)

    if form_is_valid:
        user = User.query.filter_by(id=form.get('user_id')).first()
        group = Group.query.filter_by(id=form.get('group_id')).first()
        join_group(user, group)

    users = User.query.all()
    return flask.render_template('debug/participations.html.jinja2', users=users, errors=errors)

@app.route('/debug/messages')
def debug_send():

    form = flask.request.form
    form_is_valid, errors = is_debug_msg_form_valid(form)

    if form_is_valid:
        # POST method
        create_message(
            content=form.get('msg'),
            user=User.query.filter_by(id=form.get('user_id')).first(),
            group=Group.query.filter_by(id=form.get('group_id')).first()
        )
    # GET method

    groups = Group.query.all()

    return flask.render_template('debug/msg.html.jinja2', groups=groups)

#form is invalid if: user or group doesn't exist, user is not in group, msg is empty
def is_msg_form_valid(form):
    result = True
    errors = []


    # user_id = form.get('user_id', "")
    # if user_id == "":
    #     result = False
    #     errors += ['user field is empty']
    # else:
    #     user = User.query.filter_by(id=user_id).first()
    #     if user == "":
    #         result = False
    #         errors += ['user does not exist']

    group_id = form.get('group_id', "")
    if group_id == "":
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

    # if result and not is_in_group(user_id, group_id):
    #     result = False
    #     errors += ['user in not in group']

    print("############", errors)
    return result, errors

def is_login_form_valid(form):
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

    return result, errors

def is_debug_msg_form_valid(form):
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
    if group_id == "":
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

def is_debug_part_form_valid(form):
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
    if group_id == "":
        result = False
        errors += ['group field is empty']
    else:
        group = Group.query.filter_by(id=group_id).first()
        if group == "":
            result = False
            errors += ['group does not exist']

    return result, errors

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

if __name__ == '__main__':
    app.run()
