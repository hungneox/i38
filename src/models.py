from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, Integer
 
# Helper to map and register a Python class a db table
Base = declarative_base()

class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    site_url =  Column(String)
    site_title = Column(String)
    description = Column(String)
 
    def __init__(self, site_url, site_title, description):
        Base.__init__(self)
        self.site_url = site_url
        self.site_title = site_title
        self.description = description
 
    def __str__(self):
        return self.site_url
 
    def __unicode__(self):
        return self.site_url
 
    @staticmethod
    def list(session):
        return session.query(Page).all()

# class Comment(Base):
#     __tablename__ = 'comment'
#   pass