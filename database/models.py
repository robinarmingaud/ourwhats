from database.database import db

group_user_table = db.Table('participation',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    users = db.relationship('User', backref='groups', secondary=group_user_table)
    messages = db.relationship('Message', backref='group')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    messages = db.relationship('Message', backref='sender')
    profile_picture = db.Column(db.Text)
    #password = db.Column(db.String(128))

    #https://realpython.com/using-flask-login-for-user-management-with-flask/
    authenticated = db.Column(db.Boolean, default=False)
    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    attachments = db.relationship('Upload', backref='message')
    #filename = db.Column(db.Text)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))