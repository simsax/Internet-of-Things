import cherrypy,json

class Temperature:
    exposed = True

    def __init__(self):
        self.logs=[]

    def convert(self, value, originalUnit, targetUnit):
        if originalUnit==targetUnit:
            return value;
        elif originalUnit=='C':
            if targetUnit=='K':
                return value+273.15
            elif targetUnit=='F':
                return value*9.0/5.0 + 32
        elif originalUnit=='K':
            if targetUnit=='C':
                return value-273.15
            elif targetUnit=='F':
                return (value-273.15)*9.0/5.0 + 32
        elif originalUnit=='F':
            if targetUnit=='C':
                return (value-32)*5.0/9.0
            elif targetUnit=='K':
                return (value-32)*5.0/9.0 + 273.15

    def GET(self, *uri, **params):
        if (len(uri)==4 and uri[0]=="converter"):
            value = float(uri[1])
            originalUnit = uri[2]
            if (originalUnit!='C' and originalUnit!='F' and originalUnit != 'K'):
                raise  cherrypy.HTTPError(400, "originalUnit can only be C,F or K")
            targetUnit = uri[3]
            if (targetUnit!='C' and targetUnit!='F' and targetUnit != 'K'):
                raise  cherrypy.HTTPError(400, "targetUnit can only be C,F or K")
            result = self.convert(value,originalUnit,targetUnit)
            return f"""{{\
                        "originalValue": {value},
                        "originalUnit": "{originalUnit}",
                        "targeTvalue": {result},
                        "targetUnit": "{targetUnit}"
                    }}"""
        elif len(uri)==1 and uri[0]=="log":
            output = []
            for log in self.logs:
                output.append(json.dumps(log))
            return "[" + ",".join(map(str,output)) + "]" 
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

    def POST(self, *uri, **params):
        if len(uri)==1 and uri[0]=="log":
            data = json.loads(cherrypy.request.body.read())
            self.logs.append(data)
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }

    cherrypy.tree.mount(Temperature(),'/',conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.engine.start()
    cherrypy.engine.block()