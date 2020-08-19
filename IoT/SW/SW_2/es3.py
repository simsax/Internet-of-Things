import cherrypy, requests, time

def register():
    payload={"deviceID":"es3","RESTuri":"/es3","MQTTtopic":"/tiot/8/es3","resource":"example"}
    r=requests.post('http://127.0.0.1:8080/devices',json=payload)
    print(r) #debug

if __name__ == '__main__':
    while True:
        register()
        time.sleep(60)