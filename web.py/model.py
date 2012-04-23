import web

db = web.database(dbn='sqlite', db='hello.db')

def get_rows():
    return db.select('hello', order='id ASC')