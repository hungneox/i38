# -*- coding: utf-8 -*-
import os
import cherrypy
from models import *
from tools import SAEnginePlugin
from tools import SATool
from tools import RelativeEnvironment
from jinja2 import Environment, FileSystemLoader, PackageLoader, Template

env = RelativeEnvironment(loader=FileSystemLoader(["templates"])) 

def authenticate():
    user = cherrypy.session.get(SESSION_KEY, None)
    if not user:
        raise cherrypy.HTTPRedirect('/login')

cherrypy.tools.authenticate = cherrypy.Tool('before_handler', authenticate)

class Root(object):

    @cherrypy.expose
    def index(self):
        pages = [page for page in Page.list(cherrypy.request.db)]
        cherrypy.response.headers['content-type'] = 'text/html'
        template = env.get_template( "index.html")
        return template.render(page_list=pages)

    @cherrypy.expose
    def page(self):
      return "This is the page content"

    @cherrypy.expose
    def login(self, username=None, password=None, from_page=None):
        if username is None or password is None:
            template = env.get_template("login.html")
            return template.render()

        error_msg = User.check_credentials(cherrypy.request.db, username, password)

        if error_msg:
            template = env.get_template( "login.html")
            return template.render(error_msg=error_msg)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            raise cherrypy.HTTPRedirect(from_page or "/")

    @cherrypy.expose
    def register(self, username=None, password=None):
        if username and password:
            user = User(username, password)
            cherrypy.request.db.add(user)
        else:
            template = env.get_template( "register.html")
            error_msg = "Username and password cannot be empty."
            return template.render(error_msg=error_msg)

    @cherrypy.expose
    @cherrypy.tools.authenticate() 
    def submit(self, page_title=None, page_url=None, description=None):
        if page_title and page_url:
            page = Page(page_title, page_url, description)
            cherrypy.request.db.add(page)
        template = env.get_template( "submit.html")
        return template.render()

    @cherrypy.expose
    def news(self, id):
        page = Page.get(cherrypy.request.db, id)
        template = env.get_template("news.html")
        return template.render(page=page)

if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()