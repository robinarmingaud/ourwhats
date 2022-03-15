import glob
import os
from datetime import datetime

import flask
from flask import redirect, url_for
from flask_login import login_required, LoginManager, login_user, current_user, logout_user
from werkzeug.utils import secure_filename
from database.database import db, init_database
from database.models import Group, User, Message, group_user_table

#https://stackoverflow.com/questions/44926465/upload-image-in-flask
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'zip'}

app = flask.Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = 'xxxxyyyyyzzzzz'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)
with app.test_request_context():
    init_database()

#cleaning all db
@app.route('/clean/all')
def db_clean_all():
    db.drop_all()
    db.create_all()

    db.session.add(User(name='OurWhats',id=0))
    db.session.commit()
    #clean_uploads()
    return "Cleaned!"

@app.route('/clean/<table>')
def db_clean_table(table):
    if table == 'users':
        users = User.query.all()
        for user in users:
            delete_user(user)
        return 'Users cleaned!'
    elif table == 'groups':
        groups = Group.query.all()
        for group in groups:
            delete_group(group)
        return 'Groups cleaned!'
    elif table == 'part':
        group_user_table.drop()
        db.create_all()
        return 'Participations cleaned!'
    elif table == 'msg' :
        clean_model_table(Message)
        #clean_uploads()
        return 'Messages cleaned !'
    return "/clean/['users', 'groups', 'part', 'msg']"

def clean_model_table(model):
    for row in model.query.all():
        db.session.delete(row)
    db.session.commit()
    db.create_all()
    return

def create_user(name):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return user

def delete_user(user):
    #we have to delete the user, its messages and its participations
    messages = Message.query.filter_by(sender_id=user.id).all()
    for msg in messages:
        db.session.delete(msg)
    participations = db.session.query(group_user_table).filter_by(user_id=user.id).all()
    for part in participations:
        db.session.delete(part)
    db.session.commit()
    return

def create_group(name):
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()

    ourwhats = User.query.filter_by(id=0).first()
    join_group(ourwhats, group)
    create_message(user=ourwhats,
                   group=group,
                   content='Nouveau groupe !',
                   filename='')
    return group

def delete_group(group):
    #we have to delete the group, its messages and its participations
    messages = Message.query.filter_by(group_id=group.id).all()
    for msg in messages:
        db.session.delete(msg)
    participations = db.session.query(group_user_table).filter_by(group_id=group.id).all()
    for part in participations:
        db.session.delete(part)
    db.session.commit()
    return

def create_message(content, user, group, filename):
    msg = Message(content=content, sender=user, group=group, date=datetime.now(), filename=filename)
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

def clean_uploads():
    files = glob.glob(UPLOAD_FOLDER)
    for f in files:
        os.remove(f)
    return

@login_required
@app.route('/<group_id>', methods=['POST','GET'])
def messages(group_id):
    groups = Group.query.all()
    active_group = Group.query.filter_by(id=group_id).one()

    form = flask.request.form
    msg_form_is_valid, errors = is_msg_form_valid(form)

    if msg_form_is_valid and flask.request.method=='POST':
        #POST method
        filename = ''
        file = flask.request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        create_message(
            content=form.get('msg'),
            user=current_user,
            group=active_group,
            filename=filename
        )

    # GET method
    return flask.render_template("main_view.html.jinja2",
                                 groups=groups, active_group=active_group, errors=errors,
                                 msg_chain=msg_chain, get_sender=get_sender) #tool functions

@app.route('/', methods=['POST','GET'])
@app.route('/login', methods=['POST','GET'])
def login():
    #GET requests display the login form
    #POST methods process the login form
    form = flask.request.form
    form_is_valid, errors = is_login_form_valid(form)

    if form_is_valid:
        user = User.query.filter_by(id=form.get('user_id')).first()
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("messages", group_id=1))

    users = User.query.all()

    return flask.render_template("logintest.html.jinja2", users=users, errors=errors)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return login()

@app.route('/debug/users', methods=['GET','POST'])
def debug_users():

    form = flask.request.form
    if flask.request.method=='POST':
        create_user(
            name=form.get('user_name')
        )
    users = User.query.all()
    return flask.render_template('debug/users.html.jinja2', users=users)

@app.route('/debug/groups', methods=['POST','GET'])
def debug_groups():

    form = flask.request.form
    if flask.request.method=='POST':
        create_group(
            name=form.get('group_name')
        )
    groups = Group.query.all()
    return flask.render_template('debug/groups.html.jinja2', groups=groups)

@app.route('/debug/part', methods=['POST','GET'])
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

@app.route('/debug/msg', methods=['POST','GET'])
@app.route('/debug/messages', methods=['POST','GET'])
def debug_messages():

    form = flask.request.form
    request = flask.request
    form_is_valid, errors = is_debug_msg_form_valid(form)

    if request.method =='POST' and form_is_valid:
        # POST method
        filename=''
        file=request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        create_message(
            content=form.get('msg'),
            user=User.query.filter_by(id=form.get('user_id')).first(),
            group=Group.query.filter_by(id=form.get('group_id')).first(),
            filename=filename
        )
    # GET method

    groups = Group.query.all()

    return flask.render_template('debug/messages2.html.jinja2', groups=groups, msg_chain=msg_chain, get_sender=get_sender)

#form is invalid if: user or group doesn't exist, user is not in group, msg is empty
def is_msg_form_valid(form):
    result = True
    errors = []

    content = form.get('msg', "")
    if content == "" :
        result = False
        errors += ['msg field is empty']

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

    content = form.get('msg', '')
    file = form.get('file', '')
    if content == "": # and file = '':
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

def allowed_file(filename):
    return ('.' in filename) and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def msg_chain(group):
    L, l = [], []
    looked_user_id = group.messages[0].sender_id
    for msg in group.messages:
        if msg.sender_id == looked_user_id:
            l.append(msg)
        else:
            L.append(l)
            l = [msg]
            looked_user_id = msg.sender_id
    L.append(l)
    return L[::-1]
    #we return the reversed list in order to display correctly the messages in the flex-direction: column-reverse

def get_sender(msg):
    users = User.query.all()
    for user in users:
        if user.id == msg.sender_id:
            return user
    print("ERREUR : can't find sender with such id :", msg.sender_id)
    return "???"



# def change_profile_pic(user, ):
#     user.has_profile_pic = True
#     db.session.add(user)
#     db.session.commit()

if __name__ == '__main__':
    app.run()
