import json, requests, time
import paho.mqtt.client as pmqtt
import threading

class Mqtt:
    def __init__(self,clientID,broker,port,topic_temperature,topic_presence,topic_noise):
        self.clientID = clientID
        self.broker = broker
        self.port = port
        self.topic_temperature = topic_temperature
        self.topic_presence = topic_presence
        self.topic_noise = topic_noise
        self.mypmqtt = pmqtt.Client(clientID, False)
        self.mypmqtt.on_connect = self.myOnConnect
        self.mypmqtt.on_message = self.myReceived
        self.temp = None
        self.pres = 0
        self.noise = 0

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def start(self):
        self.mypmqtt.connect(self.broker,int(self.port))
        self.mypmqtt.loop_start()

    def stop(self):
        self.mypmqtt.loop_stop()
        self.mypmqtt.disconnect()

    def myPublish(self, topic, message):
        self.mypmqtt.publish(topic, message, 2)

    def mySubscribe(self, topic):
        self.mypmqtt.subscribe(topic, 2)

    def myReceived (self, pmqtt , userdata, msg):
        data = json.loads(msg.payload)
        if msg.topic==self.topic_temperature:      
            self.temp = data["e"][0]["v"]
        elif msg.topic==self.topic_presence:
            self.pres = data["e"][0]["v"]
        elif msg.topic==self.topic_noise:
            self.noise = data["e"][0]["v"]

class Register(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload=payload

    def run(self):
        while True:
            r = requests.post('http://127.0.0.1:8080/services',json=self.payload)
            time.sleep(60)

if __name__ == '__main__':
    payload={"serviceID":"RemoteController","RESTuri":"/es4","MQTTtopic":"/tiot/8/es4","type":"Remote smart home controller"}
    register = Register(payload)
    register.start() #thread che ogni minuto effettua l'update della registrazione al catalog
    r = requests.get('http://127.0.0.1:8080/broker')
    data = r.json()
    broker = data['brokerIP']
    port = data['port']
    param={"deviceID":"Yun_temperature"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic_temperature = data["MQTTtopic"]
    else:
        print("Wrong data format")
    param={"deviceID":"Yun_presence"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic_presence = data["MQTTtopic"]
    else:
        print("Wrong data format")
    param={"deviceID":"Yun_noise"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic_noise = data["MQTTtopic"]
    else:
        print("Wrong data format")   
    param={"deviceID":"Yun_setpoints"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic_setpoints = data["MQTTtopic"]
    else:
        print("Wrong data format")   
    param={"deviceID":"Yun_lcd"}
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic_lcd = data["MQTTtopic"]
    else:
        print("Wrong data format") 
    mqtt=Mqtt("LabSW_3",broker,port,topic_temperature,topic_presence,topic_noise)
    mqtt.start()  
    mqtt.mySubscribe(topic_temperature)
    mqtt.mySubscribe(topic_presence)
    mqtt.mySubscribe(topic_noise)
    
    while True:
        user_input=input("Available commands: \n\
        temp: visualize temperature\n\
        pres: verify if someone is present in the room\n\
        noise: verify if there is noise in the room\n\
        setpoints: modify temperature set points\n\
        lcd: write a message on the lcd monitor\n\
        quit: exit\n")
        if user_input=="temp":
            print(f"Current temperture: {mqtt.temp} °C")
        elif user_input=="pres":
            print(f"Pres = {mqtt.pres}")
        elif user_input=="noise":
            print(f"Noise = {mqtt.noise}")
        elif user_input=="setpoints":
            setpoint=input("Set point type: ") #mi aspetto una stringa del formato definito nel file arduino 
            value=input("Set point value: ")
            message = (f'{{"bn":"Yun_setpoints","e":[{{"n":"{setpoint}","t":null,"v":{value},"u":"Cel"}}]}}')
            mqtt.myPublish(topic_setpoints,message)
            print("Set points successfully sent to the Yun")
        elif user_input=="lcd":
            text=input("Message: ")
            message = (f'{{"bn":"Yun_lcd","e":[{{"n":"lcd","t":null,"v":{text},"u":null}}]}}')
            mqtt.myPublish(topic_lcd,message)
        elif user_input=="quit":
            break
        else:
            print("Command not recognized")
    print("Goodbye!") 
    mqtt.stop()