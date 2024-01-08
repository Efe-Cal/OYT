import requests
import json
import numpy as np
def getFaceEncodings(sinif):
    login = requests.get("http://localhost:7777/login/1234")
    if login.text == "Login successful!":
        print("Login successful!")
        r = requests.get(f"http://localhost:7777/getFaceEncodings/{sinif}",cookies=login.cookies,headers=login.headers)
        data = json.loads(r.text)
        data[0] = [np.array(i) for i in data[0]]
        return data