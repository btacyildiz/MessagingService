import uuid
from flask import Flask, render_template
from ClientInfo import users

flaskapp = Flask(__name__)
flaskapp.secret_key = str(uuid.uuid4())

@flaskapp.route('/')
def page_home():
    return render_template('index.html')


@flaskapp.route("/users")
def list_users():
    html = ""
    for name in users.keys():
        html += name
    return html