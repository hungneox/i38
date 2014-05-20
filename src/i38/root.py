# -*- coding: utf-8 -*-
import cherrypy
from models import Page
from tools import SAEnginePlugin
from tools import SATool
from tools import RelativeEnvironment
from jinja2 import Environment, FileSystemLoader, PackageLoader, Template

env = RelativeEnvironment(loader=FileSystemLoader(["templates"])) 

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
    def login(self, username=None, password=None, register=False):
        template = env.get_template( "login.html")
        return template.render()

    @cherrypy.expose
    def submit(self, page_title=None, page_url=None, description=None):
        if page_title and page_url:
            page = Page(page_title, page_url, description)
            cherrypy.request.db.add(page)
        template = env.get_template( "submit.html")
        return template.render()

if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()