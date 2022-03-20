import glob
import os
from datetime import datetime

import flask
from flask import redirect, url_for
from flask_login import login_required, LoginManager, login_user, current_user, logout_user
from werkzeug.utils import secure_filename
from database.database import db, init_database
from database.models import Group, User, Message, Upload, participation_table, ProfileP

# https://stackoverflow.com/questions/44926465/upload-image-in-flask
UPLOAD_FOLDER = 'static/uploads'
PP_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'zip', 'mp4'}
ALLOWEDPP = {'jpg', 'jpeg', 'png', 'gif'}
app = flask.Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PP_FOLDER'] = PP_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = 'xxxxyyyyyzzzzz'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)
with app.test_request_context():
    init_database()


# cleaning all db
@app.route('/clean/all')
def db_clean_all():
    db.drop_all()
    db.create_all()

    db.session.add(User(name='OurWhats', id=0))
    db.session.add(ProfileP(id=0, user_id=0, filename="default.jpg"))
    db.session.commit()
    # clean_uploads()
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
        db.session.query(participation_table).drop()
        db.create_all()
        return 'Participations cleaned!'
    elif table == 'msg':
        clean_model_table(Message)
        # clean_uploads()
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
    pp = ProfileP(filename="default.jpg",
                  user_id=user.id)
    db.session.add(pp)
    db.session.commit()
    new_conv = create_group(name="Conversation")
    join_group(user,new_conv)
    return user


def delete_user(user):
    # we have to delete the user, its messages and its participations
    messages = Message.query.filter_by(sender_id=user.id).all()
    for msg in messages:
        db.session.delete(msg)
    participations = db.session.query(participation_table).filter_by(user_id=user.id).all()
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
                   content='Nouveau groupe !')
    return group


def delete_group(group):
    # we have to delete the group, its messages and its participations
    messages = Message.query.filter_by(group_id=group.id).all()
    for msg in messages:
        db.session.delete(msg)
    participations = db.session.query(participation_table).filter_by(group_id=group.id).all()
    for part in participations:
        db.session.delete(part)
    db.session.commit()
    return


def create_message(content, user, group):
    msg = Message(content=content,
                  sender=user,
                  group=group,
                  date=datetime.now())
    db.session.add(msg)
    db.session.commit()
    return msg


def create_upload(message, filename):
    upload = Upload(filename=filename,
                    message=message)
    db.session.add(upload)
    db.session.commit()
    return upload


def upload_pp(user, filename):
    old_pp = ProfileP.query.filter_by(user_id=current_user.id).one()
    db.session.delete(old_pp)
    db.session.commit()
    pp = ProfileP(filename=filename,
                  user_id=user)
    db.session.add(pp)
    db.session.commit()
    return pp


# makes an user join a group
def join_group(user, group):
    group.users.append(user)
    db.session.add(user)
    db.session.commit()
    return


# checks if an user is in a group
def is_in_group(user_id, group_id):
    return db.session.query(participation_table).filter_by(group_id=group_id, user_id=user_id).first() is not None


def clean_uploads():
    files = glob.glob(UPLOAD_FOLDER)
    for f in files:
        os.remove(f)
    return


def quit_group(user, group):
    if is_in_group(user.id, group.id) and db.session.query(participation_table).filter_by(user_id = user.id).count()>1 :
        msgs = Message.query.filter(Message.sender_id == user.id, Message.group_id == group.id).all()
        for msg in msgs:
            db.session.delete(msg)
        db.session.query(participation_table).filter_by(group_id = group.id, user_id = user.id).delete()
        db.session.commit()
    return


@login_required
@app.route('/<active_group_id>', methods=['POST', 'GET'])
def messages(active_group_id):
    groups = Group.query.all()
    if not is_in_group(current_user.id, active_group_id):
        return flask.redirect(url_for('messages', active_group_id=first_group(current_user).id))

    users = User.query.all()
    active_group = Group.query.filter(Group.id == active_group_id).one()
    update_last_read_time(current_user, active_group)
    request = flask.request
    msg_form_is_valid, errors = is_msg_form_valid(request.form)
    if ("Envoyer" in request.form) and msg_form_is_valid and request.method == 'POST':
        # POST method
        msg = create_message(
            content=request.form.get('msg'),
            user=current_user,
            group=active_group
        )
        send_attachments(request, msg)

    if ("Televerser" in request.form) and request.method == 'POST':
        send_pp(request, current_user.id)

    if ("ChangeUserName" in request.form) and request.method == 'POST' and request.form.get("changeName") != "":
        current_user.name = request.form.get("changeName")
        db.session.commit()

    if ("NewConv" in request.form) and request.method == 'POST' and request.form.get("convName") != "":
        new_group = create_group(
            name=request.form.get('convName')
        )
        join_group(current_user, new_group)
        return redirect(url_for("messages", active_group_id=active_group.id))

    if ("addMember" in request.form) and request.method == 'POST':
        join_group(User.query.filter_by(id=request.form.get("value")).one(), active_group)
        return redirect(url_for("messages", active_group_id=active_group.id))

    if ('quitGroup' in request.form) and request.method == 'POST':
        quit_group(current_user, active_group)
        return flask.redirect(url_for('messages', active_group_id=first_group(current_user).id))

    # returns the groups list ordered chronologically (by date of last msg sent)
    ordered_groups = reversed(sorted(groups, key=lambda group: group.messages[-1].date))

    # GET method
    return flask.render_template("main_view.html.jinja2",
                                 ordered_groups=ordered_groups, active_group=active_group, errors=errors, users=users,
                                 msg_chain=msg_chain, unread_messages_count=unread_messages_count,
                                 get_user_pp=get_user_pp, get_user_data=get_user_data,
                                 get_data_received=get_data_received, get_total_data=get_total_data)  # tool functions


@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    # GET requests display the login form
    # POST methods process the login form
    form = flask.request.form
    form_is_valid, errors = is_login_form_valid(form)

    if form_is_valid:
        user = User.query.filter_by(id=form.get('user_id')).first()
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("messages", active_group_id=first_group(user).id))

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


@app.route('/debug/users', methods=['GET', 'POST'])
def debug_users():
    form = flask.request.form
    if flask.request.method == 'POST':
        create_user(
            name=form.get('user_name')
        )
    users = User.query.all()
    return flask.render_template('debug/users.html.jinja2', users=users, get_user_pp=get_user_pp)


@app.route('/debug/groups', methods=['POST', 'GET'])
def debug_groups():
    form = flask.request.form
    if flask.request.method == 'POST':
        create_group(
            name=form.get('group_name')
        )
    groups = Group.query.all()
    return flask.render_template('debug/groups.html.jinja2', groups=groups)


@app.route('/debug/part', methods=['POST', 'GET'])
@app.route('/debug/participations', methods=['POST', 'GET'])
def debug_participations():
    form = flask.request.form
    form_is_valid, errors = is_debug_part_form_valid(form)

    if form_is_valid:
        user = User.query.filter_by(id=form.get('user_id')).first()
        group = Group.query.filter_by(id=form.get('group_id')).first()
        join_group(user, group)

    users = User.query.all()
    return flask.render_template('debug/participations.html.jinja2', users=users, errors=errors)


@app.route('/debug/msg', methods=['POST', 'GET'])
@app.route('/debug/messages', methods=['POST', 'GET'])
def debug_messages():
    form = flask.request.form
    request = flask.request
    form_is_valid, errors = is_debug_msg_form_valid(form)

    if request.method == 'POST' and form_is_valid:
        # POST method

        message = create_message(
            content=form.get('msg'),
            user=User.query.filter_by(id=form.get('user_id')).first(),
            group=Group.query.filter_by(id=form.get('group_id')).first()
        )
        send_attachments(request, message)

    # GET method
    groups = Group.query.all()

    return flask.render_template('debug/messages2.html.jinja2', groups=groups, msg_chain=msg_chain)


def send_attachments(request, message):
    attachments = request.files.getlist('file[]')
    for file in attachments:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            create_upload(message=message,
                          filename=filename)
    return


def send_pp(request, user):
    pp = request.files['ppfile']
    if pp and allowed_pp(pp.filename):
        filename = secure_filename(pp.filename)
        pp.save(os.path.join(app.config['PP_FOLDER'], filename))
        upload_pp(user=user,
                  filename=filename)
    return


# form is invalid if: user or group doesn't exist, user is not in group, msg is empty
def is_msg_form_valid(form):
    result = True
    errors = []

    content = form.get('msg', "")
    if content == "":
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
    if content == "":  # and file = '':
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


def allowed_pp(filename):
    return ('.' in filename) and filename.rsplit('.', 1)[1].lower() in ALLOWEDPP


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
    # we return the reversed list in order to display correctly the messages in the flex-direction: column-reverse


# adaptation du code proposé ici : https://www.codestudyblog.com/cnb2001/0123091336.html
# @app.route('/<user_id>/<group_id>', methods=['POST','GET'])
def unread_messages_count(user, group):
    last_read_time = db.session.query(participation_table).filter(
        participation_table.c.group_id == group.id,
        participation_table.c.user_id == user.id
    ).first().last_read_time

    return Message.query.filter_by(group_id=group.id). \
        filter(Message.date > last_read_time).count()


def update_last_read_time(user, group):
    db.session.query(participation_table).filter(
        participation_table.c.group_id == group.id,
        participation_table.c.user_id == user.id
    ).update({'last_read_time': datetime.now()})
    db.session.commit()
    return


# returns the first group that should be displayed on connection
def first_group(user):
    groups = Group.query.all()
    for group in groups:
        if is_in_group(user.id, group.id):
            return group


def get_user_pp(user):
    return ProfileP.query.filter_by(user_id=user.id).one().filename


def get_user_data(user):
    files = db.session.query(Upload).join(Message, Message.id == Upload.message_id).filter(
        Message.sender_id == user.id).all()
    data = 0
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        data += os.path.getsize(path)
    return round(data / 10485.76) / 100


def get_data_received(user):
    files = db.session.query(Upload).join(Message, Message.id == Upload.message_id).join(Group,
                                                                                         Message.group_id == Group.id).join(
        participation_table).filter_by(user_id=user.id).all()
    data = 0
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        data += os.path.getsize(path)
    return round(data / 10485.76) / 100


def get_total_data():
    files = db.session.query(Upload).all()
    data = 0
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        data += os.path.getsize(path)
    return round(data / 10485.76) / 100


if __name__ == '__main__':
    app.run()
