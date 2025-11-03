import os
import time
import json


config = "config.json"
datos = "datos"

def cargarConfig():
    if not os.path.exists(config):
        conf = {
            "api_url": "http://127.0.0.1:5000/getDatos", 
            "recarga": 2
        }
        guardarConfig(conf)
        with open(config, "r") as f:
            return json.load(f)
        
def guardarConfig(conf):
    with open(config, "w") as f:
        json.dump(conf, f, indent=4)

config  = cargarConfig()
os.makedirs(datos, exist_ok=True)