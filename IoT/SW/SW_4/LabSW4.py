import json, requests, time, telepot
import paho.mqtt.client as pmqtt
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import threading

data_temp = "None"
data_pres = 0
data_noise = 0
data_gas = 0

class Mqtt:
    def __init__(self,clientID,broker,port,topic_temperature,topic_presence,topic_noise,topic_gas):
        self.clientID = clientID
        self.broker = broker
        self.port = port
        self.topic_temperature = topic_temperature
        self.topic_presence = topic_presence
        self.topic_noise = topic_noise
        self.topic_gas = topic_gas
        self.mypmqtt = pmqtt.Client(clientID, False)
        self.mypmqtt.on_connect = self.myOnConnect
        self.mypmqtt.on_message = self.myReceived
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
        global data_temp
        global data_pres
        global data_noise
        global data_gas
        data = json.loads(msg.payload)
        val = data['e'][0]['v']
        if msg.topic==self.topic_temperature:       
            data_temp = f"The temperature in the room is {val} °C" #salva l'ultimo valore ricevuto in una variabile
        elif msg.topic==self.topic_presence:
            if val == 1:
                data_pres = "There is someone in the room"
            elif val == 0:
                data_pres = "There is nobody in the room"
        elif msg.topic==self.topic_noise:
            if val == 1:
                data_noise = "There is no noise in the room"
            elif val == 0:
                data_noise = "There is noise in the room"
        elif msg.topic == self.topic_gas:
            data_gas = val 

class Register(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload=payload

    def run(self):
        while True:
            r = requests.post('http://127.0.0.1:8080/services',json=self.payload)
            time.sleep(60)

class GasControl(threading.Thread):
    def __init__(self,bot):
        threading.Thread.__init__(self)
        self.userID = 165145502 #ID utente, il bot deve conoscerlo per potergli inviare i messaggi
        self.bot = bot

    def run(self):   
        while True:
            if data_gas > 0.04: #concentrazione gas superiore al 4%
                self.bot.bot.sendMessage(self.userID, "ATTENZIONE! Concentrazione di gas troppo alta")
            time.sleep(60)

class MyBot:
    def __init__(self,token,mqtt,topic_lcd,topic_setpoints):
        self.token = token
        self.bot = telepot.Bot(token)
        self.mqtt = mqtt
        self.topic_lcd = topic_lcd
        self.topic_setpoints = topic_setpoints
        self.sp = 0
        self.lcd = 0
        self.sptype = None

    def on_chat_message(self,msg):
        content_type, chat_type, chat_id = telepot.glance(msg) #ottiene parametri conversazione e id della chat

        command = msg['text']
        if self.sp == 0 and self.lcd == 0:
            if command == "/start":
                self.bot.sendMessage(chat_id,"Available commands: \n\n/temp: visualize temperature\n/pres: verify if someone is present in the room\n/noise: verify if there is noise in the room\n/setpoints: modify temperature set points\n/lcd: write a message on the lcd monitor\n")
            elif command == "/temp":
                self.bot.sendMessage(chat_id, data_temp)
            elif command == "/pres":
                self.bot.sendMessage(chat_id, data_pres)
            elif command == "/noise":
                self.bot.sendMessage(chat_id, data_noise)
            elif command == "/setpoints":
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="fm0",callback_data="fm0"),InlineKeyboardButton(text="fM0",callback_data="fM0"),InlineKeyboardButton(text="lm0",callback_data="lm0"),InlineKeyboardButton(text="lM0",callback_data="lM0")],
                                [InlineKeyboardButton(text="fm1",callback_data="fm1"),InlineKeyboardButton(text="fM1",callback_data="fM1"),InlineKeyboardButton(text="lm1",callback_data="lm1"),InlineKeyboardButton(text="lM1",callback_data="lM1")]
                            ])
                self.bot.sendMessage(chat_id, "Choose the set-point", reply_markup=keyboard)
            elif command == "/lcd":
                self.bot.sendMessage(chat_id, "Send the message you want to display on the monitor")
                self.lcd = 1
        elif self.sp == 1: #l'utente ha inserito il valore del set-point
            spvalue = msg['text']
            message = (f'{{"bn":"Yun_setpoints","e":[{{"n":"{self.sptype}","t":null,"v":{spvalue},"u":"Cel"}}]}}')
            self.mqtt.myPublish(self.topic_setpoints,message)
            self.bot.sendMessage(chat_id, "Set points successfully sent to the Yun")
            self.sp = 0
        elif self.lcd == 1: #l'utente ha inserito il messaggio da inviare al monitor
            text = msg['text']
            message = (f'{{"bn":"Yun_lcd","e":[{{"n":"lcd","t":null,"v":"{text}","u":null}}]}}')
            self.mqtt.myPublish(self.topic_lcd,message)
            self.bot.sendMessage(chat_id, "Message successfully displayed on the monitor")
            self.lcd = 0

    def on_callback_query(self,msg):
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data != "lcd":
            self.sp = 1
            self.sptype = query_data
            self.bot.sendMessage(chat_id, "Send the set-point value")

    def start(self):
        MessageLoop(self.bot,{'chat':self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
        while True:
            time.sleep(1)

if __name__ == '__main__':
    payload={"serviceID":"RemoteController","RESTuri":"/es1","MQTTtopic":"/tiot/8/es1","type":"Remote smart home controller"}
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
    param={"deviceID":"GasSensor"} 
    r = requests.get('http://127.0.0.1:8080/devices/registered',param)
    data = r.json()
    if "MQTTtopic" in data:
        topic_gas = data["MQTTtopic"]
    else:
        print("Wrong data format")
  
    mqtt=Mqtt("LabSW_4",broker,port,topic_temperature,topic_presence,topic_noise,topic_gas)
    mqtt.start()  
    mqtt.mySubscribe(topic_temperature)
    mqtt.mySubscribe(topic_presence)
    mqtt.mySubscribe(topic_noise)
    mqtt.mySubscribe(topic_gas)
    token = "1373323804:AAEr6e14Bz5zEuPQRTcqwh0xTSg58PRSeZ0" #token del bot
    bot = MyBot(token,mqtt,topic_lcd,topic_setpoints)
    gasController = GasControl(bot)
    gasController.start()
    bot.start()
    mqtt.stop()