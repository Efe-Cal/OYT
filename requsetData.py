import requests
import json
import numpy as np
def getFaceEncodings(sinif,host,port,password):
    login = requests.get(f"http://{host}:{port}/login/{password}")
    if login.text == "Login successful!":
        print("Login successful!")
        r = requests.get(f"http://{host}:{port}/getFaceEncodings/{sinif}",cookies=login.cookies,headers=login.headers)
        data = json.loads(r.text)
        data[0] = [np.array(i) for i in data[0]]
        return data
def getDersProg(sinif,host,port,password):
    login = requests.get(f"http://{host}:{port}/login/{password}")
    if login.text == "Login successful!":
        print("Login successful!")
        r = requests.get(f"http://{host}:{port}/dersprog/{sinif}",cookies=login.cookies,headers=login.headers)
        data = json.loads(r.content)
        return data