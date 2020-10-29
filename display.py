from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
@app.route('/<title>')
def index(title=''):
    return render_template('navigation.html', title=title)
