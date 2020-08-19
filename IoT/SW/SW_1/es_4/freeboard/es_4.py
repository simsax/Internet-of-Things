import cherrypy, json, os

class Dashboard:
    exposed = True

    def GET(self,*uri,**params):
        return open("index.html").read()

    def POST(self,*uri,**params):
        if uri[0] == "saveDashboard":
            with open("dashboard/dashboard.json", "w") as file:
                file.write(params['json_string'])

if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True,
            'tools.staticdir.root':os.getcwd(),
        },
       "/css":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"css"
        },
        "/js":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"js"
        },
        "/img":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"img"
        },
        "/plugins":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"plugins"
        },
        "/dashboard":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"dashboard"
        }
    }

    try:
        cherrypy.tree.mount(Dashboard(),'/',conf)
        cherrypy.engine.start()
        cherrypy.engine.block()
    except KeyboardInterrupt:
        test.end()