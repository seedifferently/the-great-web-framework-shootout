# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose

from helloworld.lib.base import BaseController
from helloworld.model import DBSession, metadata
from helloworld.controllers.error import ErrorController
from helloworld import model

__all__ = ['RootController']


class RootController(BaseController):

    # RAW STRING TEST
    @expose()
    def index(self):
        """Handle the front-page."""
        return 'Hello World!'


    # TEMPLATE TESTS
#    @expose('genshi:helloworld.templates.hello')
#    def genshi_hello(self):
#        return dict()

#    @expose('mako:hello.mak')
#    def mako_hello(self):
#        return dict()

    @expose('jinja:hello.jinja')
    def jinja_hello(self):
        return dict()


    # DATABASE TESTS
    @expose()
    def raw_sql(self):
        output = []
        hello = DBSession.query(model.Hello).all()
        for row in hello:
            output.append('%s - %s' % (row.id, row.data))
        return '\n'.join(output)
    
#    @expose('genshi:helloworld.templates.db')
#    def genshi_sql(self):
#        hello = DBSession.query(model.Hello).all()
#        return dict(hello=hello)

#    @expose('mako:db.mak')
#    def mako_sql(self):
#        hello = DBSession.query(model.Hello).all()
#        return dict(hello=hello)

    @expose('jinja:db.jinja')
    def jinja_sql(self):
        hello = DBSession.query(model.Hello).all()
        return dict(hello=hello)


