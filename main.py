import os
import time
import subprocess
import requests
import threading
import json
from datetime import datetime

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


def descargarDatos():
    ultimoArchivo = None
    while True:
        try: 
            print("n\Descargando datos de la api")
            r = requests.get(config["api_url"], timeout= 10)

            if r.status_code == 200:
                dato = r.json()
                if dato != ultimoArchivo:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombreArchivo = os.path.join(datos, f"contqctos{timestamp}.json")
                    with open(nombreArchivo, "w") as f:
                        json.dump(dato, f, indent=4)
                    ultimoArchivo = dato
                    print(f"Datos guardados en {nombreArchivo}")
                else:
                        print("No hay nuevos datos para guardar.")
            else:
                    print(f"Error al descargar datos: {r.status_code}")
        except Exception as e:  
            print(f"error {e}")

time.sleep(config["recarga"]) * 60

def mostrarFicheros():
     ficheros = sorted(os.listdir(datos))
     if not ficheros:
          print("no hay ficheros")
          return[]
     print("\n ficheros:")
     for i, f in enumerate(ficheros, 1):
          print(f"{i}. {f}")
          return ficheros
     
def seleccionarFichero():
          ficheros = mostrarFicheros()
          if not ficheros:
               return None
          eleccion = input("\n Numero o nombre del fichero: ")
          if eleccion.isdigit():
               idx = int(eleccion) -1
               if 0 <= idx <len(ficheros):
                    return os.path.join(datos, ficheros[idx])
               elif eleccion in ficheros:
                    return os.path.join(datos, eleccion)
               print("fichero no encontrado")
               return None
          
def verFichero():
     ruta = seleccionarFichero()
     if ruta:
          with open(ruta, "r", encoding="utf-8") as f:
               contenido = json.load(f)
               print(json.dumps(contenido, indent=2, ensure_ascii= False))
          
def ver_fichero():
    """Muestra en pantalla el contenido JSON de un fichero"""
    ruta = seleccionar_fichero()
    if ruta:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = json.load(f)
            print(json.dumps(contenido, indent=2, ensure_ascii=False))        
        