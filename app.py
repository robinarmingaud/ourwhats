from flask import Flask
from database.database import db, init_database

app = Flask(__name__)
db.init_app(app)
with app.test_request_context():
    init_database()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

@app.route('/login')
def login():  # put application's code here
    return flask.render_template("login.html.jinja2")


if __name__ == '__main__':
    app.run()
