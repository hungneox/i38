# -*- coding: utf-8 -*-
import os
import cherrypy
import urllib
from models import *
from tools import SAEnginePlugin
from tools import SATool
from tools import RelativeEnvironment
from tools import Utility
from jinja2 import Environment, FileSystemLoader, PackageLoader, Template

env = RelativeEnvironment(loader=FileSystemLoader(["templates"])) 

def authenticate():
    user = cherrypy.session.get(SESSION_KEY, None)
    get_parmas =  urllib.parse.quote(cherrypy.request.request_line.split()[1])
    if not user:
        raise cherrypy.HTTPRedirect('/login?from_page=%s' % get_parmas)

cherrypy.tools.authenticate = cherrypy.Tool('before_handler', authenticate)

class BaseController:
    def render(self, name, **data):
        template = env.get_template(name+".html")
        username = cherrypy.session.get(SESSION_KEY, None)
        data['is_user_logged_in'] = False
        if username:
            data['is_user_logged_in'] = True
            data['username'] = username
        
        return template.render(data)

class Root(BaseController):

    @cherrypy.expose
    def index(self):
        pages = [page for page in Page.list()]
        return self.render("index",page_list=pages)

    @cherrypy.expose
    def lastest(self):
      return "This is the  page content"

    @cherrypy.expose
    def login(self, username=None, password=None, from_page='/'):
        if username is None or password is None:
            return self.render('login', from_page=from_page)

        error_msg = User.check_credentials(username, password)

        if error_msg:
            return self.render("login",error_msg=error_msg)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
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
            page = Page(page_title, page_url, description)
            cherrypy.request.db.add(page)
        return self.render('submit')

    @cherrypy.expose
    def news(self, id):
        page = Page.get(id)
        return self.render("news",page=page)

    @cherrypy.expose
    def user(self, username, email=None, password=None, description=None):
        me = cherrypy.session.get(SESSION_KEY, None)
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

if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()