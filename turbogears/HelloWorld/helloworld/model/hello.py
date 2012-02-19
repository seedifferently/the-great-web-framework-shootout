# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from helloworld.model import DeclarativeBase, metadata, DBSession


class Hello(DeclarativeBase):
    __tablename__ = 'hello'
    
    def __init__(self, id, data):
        self.id = id
        self.data = data
    
    #{ Columns
    
    id = Column(Integer, primary_key=True)
    data = Column(Unicode(255), nullable=False)
    
    #}
