from flask import Flask, flash
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = 'heisenberg'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Loginto12@localhost/control'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def urlencode_filter(s):
    return quote(s)

app.jinja_env.filters['urlencode'] = urlencode_filter

if __name__ == '__main__':
    app.run(debug=True)