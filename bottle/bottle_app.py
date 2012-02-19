import os
import sqlite3
#from bottle import run
from bottle import route
from bottle import jinja2_template as template


@route('/')
def index():
    return 'Hello World!'

@route('/jinja_hello')
def hello():
    return template('templates/hello')

@route('/jinja_sql')
def hellodb():
    db = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__))) + '/hello.db')
    
    rows = db.execute('select id, data from hello order by id asc')
    lipsum = [dict(id=row[0], data=row[1]) for row in rows.fetchall()]
    
    return template('templates/db', hello=lipsum)


#if __name__ == '__main__':
#    from bottle import debug
#    debug(True)
#    run(host='localhost', port=8080)
