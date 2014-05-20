from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, Integer, Numeric, DateTime
from datetime import datetime
# Helper to map and register a Python class a db table
Base = declarative_base()

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
        self.create_at = datetime.now()

 
    def __str__(self):
        return self.site_url
 
    def __unicode__(self):
        return self.site_url
 
    @staticmethod
    def list(session):
        return session.query(Page).all()

    @staticmethod
    def get(session, id):
        return session.query(Page).get(id)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))
    description = Column(String(2048))
    create_at = Column(DateTime)

    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def __str__(self):
        return self.site_url
 
    def __unicode__(self):
        return self.site_url

    @staticmethod
    def list(session):
        return session.query(User).all()

    @staticmethod
    def get(session, id):
        return session.query(User).get(id)
# class Comment(Base):
#     __tablename__ = 'comment'
#   pass