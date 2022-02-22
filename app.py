from flask import Flask
import flask

app = Flask(__name__)


@app.route('/login')
def login():  # put application's code here
    return flask.render_template("login.html.jinja2")


if __name__ == '__main__':
    app.run()
