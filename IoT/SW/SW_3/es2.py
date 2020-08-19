import json, requests, time
import paho.mqtt.client as pmqtt

class Subscriber:
    def __init__(self,clientID,topic,broker,port):
        self.clientID = clientID
        self.topic = topic
        self.broker = broker
        self.port = port
        self.mypmqtt = pmqtt.Client(clientID, False)
        self.mypmqtt.on_message = self.myReceived
        self.mypmqtt.on_connect = self.myOnConnect

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def start(self):
        self.mypmqtt.connect(self.broker,int(self.port))
        self.mypmqtt.loop_start()
        self.mypmqtt.subscribe(self.topic, 2)

    def stop(self):
        self.mypmqtt.unsubscribe(self.topic)
        self.mypmqtt.loop_stop()
        self.mypmqtt.disconnect()

    def myReceived (self, pmqtt , userdata, msg):
        print(str(msg.payload))

if __name__ == '__main__':
    payload={"serviceID":"es2","RESTuri":"/es2","MQTTtopic":"/tiot/8/es2","type":"Temperature reader"}
    r = requests.post('http://127.0.0.1:8080/services',json=payload)
    r = requests.get('http://127.0.0.1:8080/broker')
    data = r.json()
    broker = data['brokerIP']
    port = data['port']
    param={"deviceID":"Yun_temperature"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic = data["MQTTtopic"]
    else:
        print("Yun not connected to the catalog")
        quit()
    subscriber = Subscriber("es2",topic,broker,port)
    subscriber.start()
    while True:
        time.sleep(60)
        requests.post('http://127.0.0.1:8080/services',json=payload) #per rimanere connesso al catalog
    subscriber.stop()