import cherrypy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText, Integer, Numeric, DateTime
from datetime import datetime
import hashlib

# Helper to map and register a Python class a db table
Base = declarative_base()

SESSION_KEY = '_cp_username'

class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    page_title = Column(String(200))
    page_url =  Column(String(2048))
    description = Column(String(2048))
    up = Column(Integer)
    down = Column(Integer)
    rank = Column(Numeric(12,2))
    created_at = Column(DateTime)

    def __init__(self, page_title, page_url, description):
        Base.__init__(self)
        self.page_url = page_url
        self.page_title = page_title
        self.description = description
        self.up = 0
        self.down = 0
        self.rank = 0
        self.created_at = datetime.now()

 
    def __str__(self):
        return self.site_url
 
    def __unicode__(self):
        return self.site_url
 
    @staticmethod
    def list():
        return cherrypy.request.db.query(Page).all()

    @staticmethod
    def get(id):
        return cherrypy.request.db.query(Page).get(id)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))
    description = Column(String(2048))
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
    parent_id = Column(Integer)
    page_id = Column(Integer)
    user_id = Column(Integer)
    path = Column(String(1024))
    text = Column(UnicodeText)
    created_at = Column(DateTime)

    def __init__(self, page_id, parent_id, user_id, text):
        self.page_id = page_id
        self.parent_id = parent_id
        self.user_id = user_id
        self.text = text
        self.created_at = datetime.now()

    def __str__(self):
        return self.text
 
    def __unicode__(self):
        return self.text
