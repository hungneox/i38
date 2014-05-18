import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
from models import Page
from tools import SAEnginePlugin
from tools import SATool

lookup = TemplateLookup(directories=['html'])

class Root(object):
    @cherrypy.expose
    def index(self):
        # host = cherrypy.request.headers['Host']
        # return "You have successfully reached " + host
        pages = [str(page) for page in Page.list(cherrypy.request.db)]
        cherrypy.response.headers['content-type'] = 'text/plain'
        return "Here are your list of messages: %s" % '\n'.join(pages)
        # tmpl = lookup.get_template("index.html")
        # return tmpl.render(salutation="Hello", target="World")

    @cherrypy.expose
    def page(self):
      return "This is the page content"

if __name__ == '__main__':
    SAEnginePlugin(cherrypy.engine, 'mysql+pymysql://root@127.0.0.1/bangtin').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Root(), '/', {'/': {'tools.db.on': True}})
    cherrypy.engine.start()
    cherrypy.engine.block()
    # cherrypy.quickstart(Root(), '/', 'server.conf')