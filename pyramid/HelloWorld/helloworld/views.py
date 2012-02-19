from pyramid.response import Response
from helloworld.models import DBSession
from helloworld.models import Hello

# RAW STRING TEST
def string_hello(context, request):
    return Response('Hello World!')

def jinja_hello(self):
    return dict()

# DATABASE TESTS
def raw_sql(self):
    output = []
    hello = DBSession.query(Hello).all()
    for row in hello:
        output.append('%s - %s' % (row.id, row.data))
    return Response('\n'.join(output))

def jinja_sql(self):
    hello = DBSession.query(Hello).all()
    return dict(hello=hello)
