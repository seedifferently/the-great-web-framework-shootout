#import transaction

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.exc import IntegrityError
#from sqlalchemy.orm.exc import NoResultFound

#from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Column

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Hello(Base):
    __tablename__ = 'hello'
    
    def __init__(self, id, data):
        self.id = id
        self.data = data
    
    #{ Columns
    
    id = Column(Integer, primary_key=True)
    data = Column(Unicode(255), nullable=False)
    
    #}

class MyApp(object):
    __name__ = None
    __parent__ = None

    def __getitem__(self, key):
        session= DBSession()
        try:
            id = int(key)
        except (ValueError, TypeError):
            raise KeyError(key)

        query = session.query(Hello).filter_by(id=id)

        try:
            item = query.one()
            item.__parent__ = self
            item.__name__ = key
            return item
        except NoResultFound:
            raise KeyError(key)

    def get(self, key, default=None):
        try:
            item = self.__getitem__(key)
        except KeyError:
            item = default
        return item

    def __iter__(self):
        session= DBSession()
        query = session.query(Hello)
        return iter(query)

root = MyApp()

def get_root(request):
    return root

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    
    return DBSession

def appmaker(engine):
    initialize_sql(engine)
    return get_root
