import time
import paho.mqtt.client as pmqtt

class Publisher:
    def __init__(self,clientID):
        self.clientID = clientID
        self.mypmqtt = pmqtt.Client(clientID, False)
        self.mypmqtt.on_connect = self.myOnConnect

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def start(self):
        self.mypmqtt.connect("test.mosquitto.org",1883)
        self.mypmqtt.loop_start()

    def stop(self):
        self.mypmqtt.loop_stop()
        self.mypmqtt.disconnect()

    def myPublish(self, topic, message):
        self.mypmqtt.publish(topic, message, 2)

if __name__ == '__main__':
    publisher = Publisher("Es6")
    publisher.start()
    while True:
        message = ('{"deviceID":"example6","RESTuri":"/es6","MQTTtopic":"tiot/8/es6","resource":"debugging"}')
        publisher.myPublish ('/tiot/8/devices', message) 
        time.sleep(60)
    publisher.stop()