# -*- coding: utf-8 -*-
import cherrypy
from models import Page
from tools import SAEnginePlugin
from tools import SATool

from jinja2 import Environment, FileSystemLoader, PackageLoader, Template

env = Environment(loader=FileSystemLoader(["/Users/hungnq/code/python/i38/src/templates"])) 

class Root(object):
    @cherrypy.expose
    def index(self):
        # host = cherrypy.request.headers['Host']
        # return "You have successfully reached " + host
        pages = [page for page in Page.list(cherrypy.request.db)]
        cherrypy.response.headers['content-type'] = 'text/html'
        template = env.get_template( "index.html")
        return template.render(page_list=pages)

    @cherrypy.expose
    def page(self):
      return "This is the page content"

if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
    # cherrypy.quickstart(Root(), '/', 'server.conf')