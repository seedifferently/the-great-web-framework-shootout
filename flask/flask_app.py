import os
import sqlite3
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'

@app.route('/jinja_hello')
def hello():
    return render_template('hello.html')

@app.route('/jinja_sql')
def hellodb():
    db = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__))) + '/hello.db')
    
    rows = db.execute('select id, data from hello order by id asc')
    lipsum = [dict(id=row[0], data=row[1]) for row in rows.fetchall()]
    
    return render_template('db.html', hello=lipsum)


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
