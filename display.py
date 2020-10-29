from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return 'Index page'


@app.route('/<test>')
def hello(test):
    return test
