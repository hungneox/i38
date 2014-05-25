# -*- coding: utf-8 -*-
import os
import cherrypy
import urllib
import json
import time
from tld import get_tld
from models import *
from tools import SAEnginePlugin
from tools import SATool
from tools import RelativeEnvironment
from utility import Utility
from jinja2 import Environment, FileSystemLoader, PackageLoader, Template

env = RelativeEnvironment(loader=FileSystemLoader(["templates"]))

def authenticate():
    user = cherrypy.session.get(SESSION_USERNAME, None)
    get_parmas =  urllib.parse.quote(cherrypy.request.request_line.split()[1])
    if not user:
        raise cherrypy.HTTPRedirect('/login?from_page=%s' % get_parmas)

cherrypy.tools.authenticate = cherrypy.Tool('before_handler', authenticate)

class BaseController:
    def render(self, name, **data):
        template = env.get_template(name+".html")
        username = cherrypy.session.get(SESSION_USERNAME, None)
        data['is_user_logged_in'] = False
        if username:
            data['is_user_logged_in'] = True
            data['username'] = username

        return template.render(data).encode('utf-8')

class Root(BaseController):
    def __init__(self):
        self.api = Api()

    @cherrypy.expose
    def index(self, page=1):
        page_size = 10
        offset = (int(page)-1) * page_size
        news_list =  News.list(page_size, offset)
        next_page = int(page)+1
        return self.render("index",news_list=news_list, next_page=next_page)

    @cherrypy.expose
    def lastest(self, page=1):
      page_size = 10
      offset = (int(page)-1) * page_size
      news_list =  News.lastest(page_size, offset)
      next_page = int(page)+1
      return self.render("index",news_list=news_list, next_page=next_page)

    @cherrypy.expose
    def login(self, username=None, password=None, from_page='/'):
        if username is None or password is None:
            return self.render('login', from_page=from_page)

        error_msg = User.check_credentials(username, password)
        user = User.find_by_username(username)
        if error_msg:
            return self.render("login",error_msg=error_msg)
        else:
            cherrypy.session[SESSION_USERNAME] = cherrypy.request.login = username
            cherrypy.session[SESSION_USER_ID]  = user.id
            raise cherrypy.HTTPRedirect(from_page or "/")

    @cherrypy.expose
    def register(self, username=None, password=None):
        if username and password:
            user = User(username, password)
            cherrypy.request.db.add(user)
        else:
            error_msg = "Username and password cannot be empty."
            return self.render("register", error_msg=error_msg)

    @cherrypy.expose
    @cherrypy.tools.authenticate()
    def submit(self, page_title=None, page_url=None, description=None):
        if page_title and page_url:
            user_id = cherrypy.session.get(SESSION_USER_ID, None)
            news = News(user_id, page_title, page_url, description)
            cherrypy.request.db.add(news)
            cherrypy.request.db.flush()
            cherrypy.request.db.refresh(news)
            raise cherrypy.HTTPRedirect('/news/%d' % news.id)
        return self.render('submit')

    @cherrypy.expose
    def news(self, id):
        news = News.get(id)
        username = cherrypy.session.get(SESSION_USERNAME, None)
        is_user_logged_in = False
        if username:
            is_user_logged_in = True
        comments =  [comment for comment in Comment.list(id)]
        return self.render("news",news=news, is_user_logged_in=is_user_logged_in, comments=comments)

    @cherrypy.expose
    def reply(self, news_id, comment_id):
      comment = Comment.get(comment_id)
      return self.render("reply", comment=comment, news_id=news_id, parent_id=comment_id,comment_id=-1)

    @cherrypy.expose
    def user(self, username, email=None, password=None, description=None):
        me = cherrypy.session.get(SESSION_USERNAME, None)
        is_my_username = False
        if me == username:
            is_my_username = True

        user = User.find_by_username(username)

        msg = None
        if not user:
            msg = "Non existing user"
        else:
            user.created_time_ago = Utility.time_ago(user.created_at)
        return self.render('user', user=user, is_me=is_my_username, error_msg=msg)

@cherrypy.popargs('api')
class Api(object):
    @cherrypy.expose
    def index(self, name, title):
        return 'About %s by %s...' % (title, name)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def post_comment(self, news_id, comment_id, parent_id, text):
        try:
          #data = cherrypy.request.json
          user_id = cherrypy.session[SESSION_USER_ID]
          comment = Comment(user_id, news_id, parent_id, text)
          news = News.get(news_id)
          news.comments += 1
          cherrypy.request.db.add(comment)
          cherrypy.request.db.flush()
          cherrypy.request.db.refresh(comment)
          if comment.parent.path:
            path = comment.parent.path + '/' + str(comment.id)
          else:
            path = str(news_id) + '/' + str(comment.id)
          level = len(path.split("/"))
          cherrypy.request.db.query(Comment).filter_by(id=comment.id).update({"path":path,"level":level})
        except Exception as ex:
          return {"success": False,"news_id": news_id, "message": str(ex)}

        return {"success": True, "comment_id": str(comment.id), "news_id": news_id}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vote_news(self, news_id, direction):
      try:
        news = News.get(news_id)
        if direction == 'up':
          news.vote_up += 1
        elif direction == 'down':
          news.vote_down += 1
        news.rank = News._rank(news.vote_up, news.vote_down, int(time.time()))
      except Exception as ex:
        return {"success": False, "news_id": news_id, "message": str(ex)}
      return {"success": True, "news_id": news_id}


if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin?charset=utf8').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
