import json, requests, time
import paho.mqtt.client as pmqtt

class Publisher:
    def __init__(self,clientID,topic,broker,port):
        self.clientID = clientID
        self.topic = topic
        self.broker = broker
        self.port = port
        self.mypmqtt = pmqtt.Client(clientID, False)
        self.mypmqtt.on_connect = self.myOnConnect

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def start(self):
        self.mypmqtt.connect(self.broker,int(self.port))
        self.mypmqtt.loop_start()

    def stop(self):
        self.mypmqtt.loop_stop()
        self.mypmqtt.disconnect()

    def myPublish(self, message):
        self.mypmqtt.publish(self.topic, message, 2)

if __name__ == '__main__':
    payload={"serviceID":"es3","RESTuri":"/es3","MQTTtopic":"/tiot/8/es3","type":"Led switcher"}
    r = requests.post('http://127.0.0.1:8080/services',json=payload)
    r = requests.get('http://127.0.0.1:8080/broker')
    data = r.json()
    broker = data['brokerIP']
    port = data['port']
    param={"deviceID":"Yun_led"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic = data["MQTTtopic"]
    else:
        print("Yun not connected to the catalog")
        quit()
    publisher = Publisher("es3",topic,broker,port)
    publisher.start()
    while True: #accendi e spegni il led ogni 30 secondi
        message = ('{"bn":"Yun","e":[{"n":"led","t":null,"v":1,"u":null}]}')
        publisher.myPublish(message)
        time.sleep(30)
        message = ('{"bn":"Yun","e":[{"n":"led","t":null,"v":0,"u":null}]}')
        publisher.myPublish(message)
        time.sleep(30)
        requests.post('http://127.0.0.1:8080/services',json=payload) #per rimanere connesso al catalog
    publisher.stop()