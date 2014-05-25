# -*- coding: utf-8 -*-
import cherrypy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText, Integer, Numeric, DateTime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import func
from datetime import datetime
import hashlib

# Helper to map and register a Python class a db table
Base = declarative_base()

SESSION_USERNAME = '_session_username'
SESSION_USER_ID  = '_session_user_id'

class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    page_title = Column(UnicodeText(200))
    page_url =  Column(String(2048))
    description = Column(UnicodeText(2048))
    vote_up = Column(Integer, default=0)
    vote_down = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    rank = Column(Numeric(12,2))
    created_at = Column(DateTime)

    user = relationship('User', foreign_keys='Page.user_id')

    def __init__(self, user_id, page_title, page_url, description):
        Base.__init__(self)
        self.user_id = user_id
        self.page_url = page_url.encode('utf-8')
        self.page_title = page_title.encode('utf-8')
        self.description = description.encode('utf-8')
        self.up = 0
        self.down = 0
        self.rank = 0
        self.created_at = datetime.now()


    def __str__(self):
        return self.site_url

    def __unicode__(self):
        return self.site_url

    @staticmethod
    def list(page_size, offset):
        return cherrypy.request.db.query(Page).limit(page_size).offset(offset)

    @staticmethod
    def get(id):
        return cherrypy.request.db.query(Page).get(id)

    @staticmethod
    def count():
      #http://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
      return  cherrypy.request.db.query(func.count(Page.id)).scalar()#optimize to count rows

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))
    description = Column(String(2048))
    karma = Column(Integer)
    created_at = Column(DateTime)

    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.created_at = datetime.now()

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    @staticmethod
    def list():
        return cherrypy.request.db.query(User).all()

    @staticmethod
    def get(id):
        return cherrypy.request.db.query(User).get(id)

    @staticmethod
    def check_credentials(username, password):
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = cherrypy.request.db.query(User).filter_by(username=username).first()
        if user is None:
            return "Username %s is not exist" % username
        if user.password != hashed_password:
            return "Incorrect password."

    @staticmethod
    def find_by_username(username):
        user = cherrypy.request.db.query(User).filter_by(username=username).first()
        return user

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_up = Column(Integer)
    vote_down = Column(Integer)
    path = Column(String(1024))
    text = Column(UnicodeText)
    created_at = Column(DateTime)

    page = relationship('Page', foreign_keys='Comment.page_id')
    user = relationship('User', foreign_keys='Comment.user_id')

    def __init__(self, user_id, page_id, parent_id, text):
        self.user_id = user_id
        self.page_id = page_id
        self.parent_id = parent_id
        self.text = text
        self.created_at = datetime.now()

    def __str__(self):
        return self.text

    def __unicode__(self):
        return self.text

    @staticmethod
    def get(id):
        return cherrypy.request.db.query(Comment).get(id)

    @staticmethod
    def list(page_id):
        return cherrypy.request.db.query(Comment).filter_by(page_id=page_id).all()
