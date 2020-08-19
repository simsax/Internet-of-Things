import cherrypy, json, os, threading, time
import paho.mqtt.client as pmqtt

class Subscriber:
    def __init__(self,clientID,topic,devices,updateFile):
        self.clientID = clientID
        self.devices = devices
        self.updateFile = updateFile
        self.topic = topic
        self.mypmqtt = pmqtt.Client(clientID, False)
        self.mypmqtt.on_message = self.myReceived
        self.mypmqtt.on_connect = self.myOnConnect

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def start(self):
        self.mypmqtt.connect("test.mosquitto.org",1883)
        self.mypmqtt.loop_start()
        self.mypmqtt.subscribe(self.topic, 2)

    def stop(self):
        self.mypmqtt.unsubscribe(self.topic)
        self.mypmqtt.loop_stop()
        self.mypmqtt.disconnect()

    def myReceived (self, pmqtt , userdata, msg):
        data = json.loads(msg.payload)
        if msg.topic == "/tiot/8/devices":
            if "deviceID" and "RESTuri" and "MQTTtopic" and "resource" in data:
                self.devices[data["deviceID"]] = dict(RESTuri=data["RESTuri"],MQTTtopic=data["MQTTtopic"],resource=data["resource"],insert_timestamp=time.time())
        elif msg.topic == "/tiot/8/users":
            if "userID" and "name" and "surname" and "email" in data:
                self.devices[data["userID"]] = dict(name=data["name"],surname=data["surname"],email=data["email"])
        elif msg.topic == "/tiot/8/services":
            if "serviceID" and "RESTuri" and "MQTTtopic" and "type" in data:
                self.devices[data["serviceID"]] = dict(RESTuri=data["RESTuri"],MQTTtopic=data["MQTTtopic"],type=data["type"],insert_timestamp=time.time())
        self.updateFile()


class Broker:
    exposed = True

    def __init__(self):
        self.brokerIP = "test.mosquitto.org"
        self.brokerPort = "1883"

    def GET(self, *uri, **params):
        if len(uri) == 0:
            return f"""{{\
                        "brokerIP": "{self.brokerIP}",
                        "port": "{self.brokerPort}"
                    }}"""
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

class Controller(threading.Thread):
    def __init__(self, devices, updateFile):
        threading.Thread.__init__(self)
        self.devices=devices
        self.updateFile = updateFile

    def run(self):
        while True:
            for key in list(self.devices):
                if (time.time()-self.devices[key]["insert_timestamp"])>120:
                    self.devices.pop(key)
                    self.updateFile()
            time.sleep(60)

class Devices:
    exposed = True

    def __init__(self):
        self.devices = dict()
        self.readFile()
        self.controller = Controller(self.devices, self.updateFile)
        self.controller.start()
        self.subscriber = Subscriber("Devices subscriber", "/tiot/8/devices",self.devices,self.updateFile)
        self.subscriber.start()

    def readFile(self):
        if os.stat('data.json').st_size != 0: #file non è vuoto
            filedict=dict()
            f = open('data.json','r')
            filedict = json.load(f)
            if "Devices" in filedict:
                self.devices = filedict["Devices"].copy()
            f.close()

    def updateFile(self):
        filedict=dict()
        if os.stat('data.json').st_size != 0:
            f=open('data.json','r') 
            filedict = json.load(f)  
            f.close()
        f=open('data.json','w')  
        filedict["Devices"] = self.devices.copy()
        json.dump(filedict, f)
        f.close()


    def GET(self, *uri, **params):
        if len(uri)==1 and uri[0]=="registered" and len(params)==0:
            if (len(self.devices)==0):
                out={"Error":"No registered devices."}
                return json.dumps(out)
            else:
                return json.dumps(self.devices)
        elif len(uri)==1 and uri[0]=="registered" and len(params)==1:
            if (len(self.devices)==0):
                out={"Error":"No registered devices."}
                return json.dumps(out)
            else:
                if "deviceID" in params:
                    if params["deviceID"] in self.devices:
                        return json.dumps(self.devices[params["deviceID"]])
                    else:
                        value=params["deviceID"]
                        out = {"Error": f"The inserted deviceID:'{value}' is not registered."}
                        return json.dumps(out)
                else:
                    raise cherrypy.HTTPError(400, "Wrong input format.")
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

    def POST(self, *uri, **params):
        if len(uri) == 0:
            data = json.loads(cherrypy.request.body.read())
            if "deviceID" and "RESTuri" and "MQTTtopic" and "resource" in data:
                self.devices[data["deviceID"]] = dict(RESTuri=data["RESTuri"],MQTTtopic=data["MQTTtopic"],resource=data["resource"],insert_timestamp=time.time())
                self.updateFile()
            else:
                raise cherrypy.HTTPError(400, "Wrong input format.")
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

class Users:
    exposed = True

    def __init__(self):
        self.users = dict()
        self.readFile()
        self.subscriber = Subscriber("Users subscriber", "/tiot/8/users",self.users,self.updateFile)
        self.subscriber.start()

    def readFile(self):
        if os.stat('data.json').st_size != 0: #file non è vuoto
            filedict=dict()
            f = open('data.json','r')
            filedict = json.load(f)
            if "Users" in filedict:
                self.users = filedict["Users"].copy()
            f.close()

    def updateFile(self):
        filedict=dict()
        if os.stat('data.json').st_size != 0:
            f=open('data.json','r')
            filedict = json.load(f)  
            f.close() 
        f=open('data.json','w') 
        filedict["Users"] = self.users.copy()
        json.dump(filedict, f)
        f.close()

    def GET(self, *uri, **params):
        if len(uri)==1 and uri[0]=="registered" and len(params)==0:
            if (len(self.users)==0):
                out={"Error":"No registered users."}
                return json.dumps(out)
            else:
                return json.dumps(self.users)
        elif len(uri)==1 and uri[0]=="registered" and len(params)==1:
            if (len(self.users)==0):
                out={"Error":"No registered users."}
                return json.dumps(out)
            else:
                if "userID" in params:
                    if params["userID"] in self.users:
                        return json.dumps(self.users[params["userID"]])
                    else:
                        value=params["userID"]
                        out = {"Error": f"The inserted userID:'{value}' is not registered."}
                        return json.dumps(out)
                else:
                    raise cherrypy.HTTPError(400, "Wrong input format.")
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

    def POST(self, *uri, **params):
        if len(uri) == 0:
            data = json.loads(cherrypy.request.body.read())
            if "userID" and "name" and "surname" and "email" in data:
                self.users[data["userID"]] = dict(name=data["name"],surname=data["surname"],email=data["email"])
                self.updateFile()
            else:
                raise cherrypy.HTTPError(400, "Wrong input format.")
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

class Services:
    exposed = True

    def __init__(self):
        self.services = dict()
        self.readFile()
        self.controller = Controller(self.services, self.updateFile)
        self.controller.start()
        self.subscriber = Subscriber("Services subscriber", "/tiot/8/services",self.services,self.updateFile)
        self.subscriber.start()

    def readFile(self):
        if os.stat('data.json').st_size != 0: #file non è vuoto
            filedict=dict()
            f = open('data.json','r')
            filedict = json.load(f)
            if "Services" in filedict:
                self.services = filedict["Services"].copy()
            f.close()

    def updateFile(self):
        filedict=dict()
        if os.stat('data.json').st_size != 0:
            f = open('data.json','r')
            filedict = json.load(f)
            f.close()    
        f = open('data.json','w')
        filedict["Services"] = self.services.copy()
        json.dump(filedict, f)
        f.close()

    def GET(self, *uri, **params):
        if len(uri)==1 and uri[0]=="registered" and len(params)==0:
            if (len(self.services)==0):
                out={"Error":"No registered services."}
                return json.dumps(out)
            else:
                return json.dumps(self.services)
        elif len(uri)==1 and uri[0]=="registered" and len(params)==1:
            if (len(self.services)==0):
                out={"Error":"No registered services."}
                return json.dumps(out)
            else:
                if "serviceID" in params:
                    if params["serviceID"] in self.services:
                        return json.dumps(self.services[params["serviceID"]])
                    else:
                        value=params["serviceID"]
                        out = {"Error": f"The inserted serviceID:'{value}' is not registered."}
                        return json.dumps(out)
                else:
                    raise cherrypy.HTTPError(400, "Wrong input format.")
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

    def POST(self, *uri, **params):
        if len(uri) == 0:
            data = json.loads(cherrypy.request.body.read())
            if "serviceID" and "RESTuri" and "MQTTtopic" and "type" in data:
                self.services[data["serviceID"]] = dict(RESTuri=data["RESTuri"],MQTTtopic=data["MQTTtopic"],type=data["type"],insert_timestamp=time.time())
                self.updateFile()
            else:
                raise cherrypy.HTTPError(400, "Wrong input format.")
        else:
            raise cherrypy.HTTPError(404, "Uri not found.")

if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }

    cherrypy.tree.mount(Broker(),'/broker',conf)
    cherrypy.tree.mount(Devices(),'/devices',conf)
    cherrypy.tree.mount(Users(),'/users',conf)
    cherrypy.tree.mount(Services(),'/services',conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.engine.start()
    cherrypy.engine.block()