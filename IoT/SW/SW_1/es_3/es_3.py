import cherrypy,json

class Temperature:
    exposed = True

    def convert(self, value, originalUnit, targetUnit):
        if originalUnit==targetUnit:
            return value
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

    def PUT(self, *uri, **params):
        content = json.loads(cherrypy.request.body.read()) #legge contenuto della richiesta PUT
        values = content["values"]
        originalUnit = content["originalUnit"]
        targetUnit = content["targetUnit"]
        results=[]
        for value in values:
            results.append(self.convert(float(value),originalUnit,targetUnit))
        return f"""{{\
                        "values": {values},
                        "originalUnit": "{originalUnit}",
                        "converted values": {results},
                        "targetUnit": "{targetUnit}"
                    }}"""

if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }

    try:
        cherrypy.tree.mount(Temperature(),'/',conf)
        cherrypy.engine.start()
        cherrypy.engine.block()
    except KeyboardInterrupt:
        test.end()