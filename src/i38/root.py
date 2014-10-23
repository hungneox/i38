# -*- coding: utf-8 -*-
import os
import cherrypy
import urllib
import json
import time
import gettext
from tld import get_tld
from models import *
from tools import SAEnginePlugin
from tools import SATool
from tools import RelativeEnvironment
from utility import Utility
from jinja2 import Environment, FileSystemLoader, PackageLoader, Template
from jinja2 import contextfunction
from jinja2.ext import Extension, i18n
from babel.core import Locale, UnknownLocaleError
from babel.support import Translations, LazyProxy

language = 'vi_VN'
domain = 'i38'

env = RelativeEnvironment(loader=FileSystemLoader(["templates"]), extensions=['jinja2.ext.i18n'])

try:
  trans = gettext.translation(domain, os.path.join(os.getcwd(), 'locales'), [language])
except IOError:
  # This probably means that there is no .mo file.
  # FIXME: This needs to be generated during installation
  trans = gettext.NullTranslations()

env.install_gettext_translations(trans)

def authenticate():
    user = cherrypy.session.get(SESSION_USERNAME, None)
    get_parmas =  urllib.parse.quote(cherrypy.request.request_line.split()[1])
    if not user:
        raise cherrypy.HTTPRedirect('/login?from_page=%s' % get_parmas)

cherrypy.tools.authenticate = cherrypy.Tool('before_handler', authenticate)

def created_at(created_at):
  now = datetime.now()
  diff = now - created_at
  mins = diff.seconds // 60
  return mins

env.globals['created_at'] = created_at

class BaseController:
    def render(self, name, **data):
        template = env.get_template(name+".html")
        username = cherrypy.session.get(SESSION_USERNAME, None)
        user_id = cherrypy.session.get(SESSION_USER_ID, None)
        data['is_user_logged_in'] = False
        data['language'] = language
        if username:
            data['is_user_logged_in'] = True
            data['username'] = username
            data['user_id'] = user_id

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
    def default(self):
      cherrypy.response.status = 404
      return self.render('404')

    @cherrypy.expose
    def help(self):
      return "Help me!"

    @cherrypy.expose
    def lastest(self, page=1):
      page_size = 10
      offset = (int(page)-1) * page_size
      news_list =  News.lastest(page_size, offset)
      next_page = int(page)+1
      return self.render("index",news_list=news_list, next_page=next_page, lastest=True)

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
    def news(self, id, **kwargs):
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
    def edit(self, news_id, comment_id):
      comment = Comment.get(comment_id)
      return self.render("edit", comment=comment, news_id=news_id, parent_id=-1,comment_id=comment_id, is_edit=True)

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

    @cherrypy.expose
    def language(self, lang='en_US', from_page=None):
      global language
      language = lang
      trans = gettext.translation(domain, os.path.join(os.getcwd(), 'locales'), [language])
      env.install_gettext_translations(trans)
      raise cherrypy.HTTPRedirect(from_page or "/")

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

          if comment.parent and comment.parent.path:
            path = comment.parent.path + '/' + str(comment.id)
          else:
            path = str(news_id) + '/' + str(comment.id)

          if int(parent_id) != -1:
            comment.sort = parent_id
          else:
            comment.sort = comment.id

          cherrypy.request.db.commit()

          level = len(path.split("/"))
          cherrypy.request.db.query(Comment).filter_by(id=comment.id).update({"path":path,"level":level})
        except Exception as ex:
          return {"success": False,"news_id": news_id, "message": str(ex)}

        return {"success": True, "comment_id": str(comment.id), "news_id": news_id}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def edit_comment(self, news_id, comment_id, parent_id, text):
      try:
        cherrypy.request.db.query(Comment).filter_by(id=comment_id).update({"text":text})
      except Exception as ex:
        return {"success": False,"news_id": news_id, "message": str(ex)}
      return {"success": True, "comment_id": str(comment_id), "news_id": news_id}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vote_news(self, news_id, direction):
      try:
        news = News.get(news_id)
        if direction == 'up':
          news.vote_up += 1
        elif direction == 'down':
          news.vote_down += 1
        news.rank = News._rank(int(news.vote_up), int(news.vote_down), int(time.time()))
      except Exception as ex:
        return {"success": False, "news_id": news_id, "message": str(ex)}
      return {"success": True, "news_id": news_id}


if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin?charset=utf8').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
