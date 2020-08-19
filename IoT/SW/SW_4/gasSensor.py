import json, requests, time,random
import paho.mqtt.client as pmqtt
import threading

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


class Register(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload=payload

    def run(self):
        while True:
            r = requests.post('http://127.0.0.1:8080/devices',json=self.payload)
            time.sleep(60)

if __name__ == '__main__':
    payload = {"deviceID":"GasSensor","RESTuri":"/gas","MQTTtopic":"/tiot/8/gas","resource":"Gas sensor"}
    register = Register(payload)
    register.start() #thread che ogni minuto effettua l'update della registrazione al catalog
    r = requests.get('http://127.0.0.1:8080/broker')
    data = r.json()
    broker = data['brokerIP']
    port = data['port']
    publisher = Publisher("GasSensor","/tiot/8/gas",broker,port)
    publisher.start()
    while True: #sensore manda valori (random) ogni minuto
        val = random.random()
        message = (f'{{"bn":"GasSensor","e":[{{"n":"gas","t":null,"v":{val},"u":null}}]}}')
        publisher.myPublish(message)
        time.sleep(60)
    publisher.stop()