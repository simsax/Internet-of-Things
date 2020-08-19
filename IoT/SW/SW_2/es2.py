import cherrypy, requests

def broker():
    try:
        r = requests.get('http://127.0.0.1:8080/broker')
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

def devices():
    try:
        r = requests.get('http://127.0.0.1:8080/devices/registered')
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

def device(deviceID):
    payload={"deviceID":deviceID}
    try:
        r = requests.get('http://127.0.0.1:8080/devices/registered',payload)
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

def users():
    try:
        r = requests.get('http://127.0.0.1:8080/users/registered')
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

def user(userID):
    payload={"userID":userID}
    try:
        r = requests.get('http://127.0.0.1:8080/users/registered',payload)
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

def services():
    try:
        r = requests.get('http://127.0.0.1:8080/services/registered')
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

def service(serviceID):
    payload={"serviceID":serviceID}
    try:
        r = requests.get('http://127.0.0.1:8080/services/registered',payload)
    except:
        print("Cannot connect to the server.\n")
    else:
        print(str(r.json()))

if __name__ == '__main__':
    while True:
        user_input=input("Available commands: \n\
        broker: the message broker\n\
        devices: all the registered devices\n\
        device: device with a specific deviceID\n\
        users: all the registered users\n\
        user: user with a specific userID\n\
        services: all the registered services\n\
        service: service with a specific serviceID\n\
        quit: exit\n")
        if user_input=="broker":
            broker()
        elif user_input=="devices":
            devices()
        elif user_input=="device":
            deviceID=input("deviceID: ")
            device(deviceID)
        elif user_input=="users":
            users()
        elif user_input=="user":
            userID=input("userID: ")
            user(userID)
        elif user_input=="services":
            services()
        elif user_input=="service":
            serviceID=input("serviceID: ")
            service(serviceID)
        elif user_input=="quit":
            break
        else:
            print("Command not recognized")
    print("Goodbye!")
