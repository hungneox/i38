# -*- coding: utf-8 -*-
import os
import cherrypy
import urllib
import json
from models import *
from tools import SAEnginePlugin
from tools import SATool
from tools import RelativeEnvironment
from tools import Utility
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
        page_size = 3
        print('page: %s' % page)
        offset = (int(page)-1) * page_size
        pages =  Page.list(page_size, offset)
        next_page = int(page)+1
        return self.render("index",pages=pages, next_page=next_page)

    @cherrypy.expose
    def lastest(self):
      return "This is the  page content"

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
            page = Page(user_id, page_title, page_url, description)
            cherrypy.request.db.add(page)
            cherrypy.request.db.flush()
            cherrypy.request.db.refresh(page)
            raise cherrypy.HTTPRedirect('/news/%d' % page.id)
        return self.render('submit')

    @cherrypy.expose
    def news(self, id):
        page = Page.get(id)
        username = cherrypy.session.get(SESSION_USERNAME, None)
        is_user_logged_in = False
        if username:
            is_user_logged_in = True
        comments =  [comment for comment in Comment.list(id)]
        return self.render("news",page=page, is_user_logged_in=is_user_logged_in, comments=comments)

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
    def post_comment(self, page_id, comment_id, parent_id, text):
        try:
          #data = cherrypy.request.json
          user_id = cherrypy.session[SESSION_USER_ID]
          comment = Comment(user_id, page_id, parent_id, text)
          cherrypy.request.db.add(comment)
        except Exception as ex:
          return {"success": False,"page_id": page_id, "message": str(ex)}

        return {"success": True, "comment_id": comment.id, "page_id": page_id}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vote_page(self, page_id, direction):
      try:
        page = Page.get(page_id)
        if direction == 'up':
          page.vote_up += 1
        elif direction == 'down':
          page.vote_down += 1
      except Exception as ex:
        return {"success": False, "page_id": page_id, "message": str(ex)}
      return {"success": True, "page_id": page_id}


if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin?charset=utf8').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
