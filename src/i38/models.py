# -*- coding: utf-8 -*-
import cherrypy
import time
from tld import get_tld
from math import log10
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, UnicodeText, Integer, Numeric, DateTime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import func
from sqlalchemy import desc
from datetime import datetime
from utility import Utility
import hashlib

# Helper to map and register a Python class a db table
Base = declarative_base()

SESSION_USERNAME = '_session_username'
SESSION_USER_ID  = '_session_user_id'

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    site_title = Column(UnicodeText(200))
    site_url =  Column(String(2048))
    description = Column(UnicodeText(2048))
    vote_up = Column(Integer, default=0)
    vote_down = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    rank = Column(Numeric(12,2))
    created_at = Column(DateTime)

    user = relationship('User', foreign_keys='News.user_id')

    def __init__(self, user_id, site_title, site_url, description):
        Base.__init__(self)
        self.user_id = user_id
        self.site_url = site_url.encode('utf-8')
        self.site_title = site_title.encode('utf-8')
        self.description = description.encode('utf-8')
        self.up = 0
        self.down = 0
        self.rank = 0
        self.created_at = datetime.now()


    def __str__(self):
        return self.site_url

    def __unicode__(self):
        return self.site_url

    def tld(self):
      return get_tld(self.site_url)

    def time_ago(self):
      return Utility.time_ago(self.created_at)

    @staticmethod
    def score(ups, downs):
      return ups - downs

    @staticmethod
    def _rank(ups, downs, date):
      # This is reddit ranking function
      # https://github.com/iangreenleaf/reddit/blob/45e8209d8d4236367a6f7247068c13ab2307afb4/r2/r2/lib/db/_sorts.pyx#L45
      s = News.score(ups, downs)
      order = log10(max(abs(s), 1))
      if s > 0:
          sign = 1
      elif s < 0:
          sign = -1
      else:
          sign = 0
      seconds = date - 1134028003
      return round((order * sign) * seconds / 45000, 7)

    @staticmethod
    def list(page_size, offset):
        return cherrypy.request.db.query(News).order_by(desc(News.rank)).limit(page_size).offset(offset)

    @staticmethod
    def lastest(page_size, offset):
       return cherrypy.request.db.query(News).order_by(desc(News.created_at)).limit(page_size).offset(offset)

    @staticmethod
    def get(id):
        return cherrypy.request.db.query(News).get(id)

    @staticmethod
    def count():
      #http://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
      return  cherrypy.request.db.query(func.count(News.id)).scalar()#optimize to count rows

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
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_up = Column(Integer)
    vote_down = Column(Integer)
    path = Column(String(255),index=True)
    level = Column(Integer, default=1)
    text = Column(UnicodeText)
    sort = Column(Integer)
    created_at = Column(DateTime)

    news = relationship('News', foreign_keys='Comment.news_id')
    user = relationship('User', foreign_keys='Comment.user_id')
    parent = relationship('Comment',  remote_side=[id])

    def __init__(self, user_id, news_id, parent_id, text):
        self.user_id = user_id
        self.news_id = news_id
        self.parent_id = parent_id
        if not self.parent_id:
          self.path = str(news_id) + '/'
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
    def list(news_id):
        return cherrypy.request.db.query(Comment).filter_by(news_id=news_id).order_by(desc(Comment.sort), Comment.path).all()

# class Comment(Base):
#     __tablename__ = 'comments'
