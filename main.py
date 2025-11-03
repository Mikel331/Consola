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
          
def editar_fichero():
    ruta = seleccionarFichero()
    if not ruta:
        return

    with open(ruta, "r", encoding="utf-8") as f:
        dato = json.load(f)

    print("1. Añadir contacto")
    print("2. Modificar contacto")
    print("3. Eliminar contacto")
    op = input("selecciona:  ")

    if op == "1":
        nuevo = {}
        nuevo["id"] = int(input("ID: "))
        nuevo["name"] = input("Nombre: ")
        nuevo["email"] = input("Email: ")
        nuevo["phone"] = input("telefono: ")
        datos.append(nuevo)
        print("Contacto añadido ")

    elif op == "2":
        modificar = int(input("ID del contacto a modificar: "))
        encontrado = next((c for c in dato if c["id"] == modificar), None)
        if encontrado:
            encontrado["name"] = input(f"Nuevo nombre ({encontrado['name']}): ") or encontrado["name"]
            encontrado["email"] = input(f"Nuevo email ({encontrado['email']}): ") or encontrado["email"]
            encontrado["phone"] = input(f"Nuevo telefono ({encontrado['phone']}): ") or encontrado["phone"]
            print("contacto actualizado ")
        else:
            print("no se encuentra")

    elif op == "3":
        eliminar = int(input("ID del contacto a eliminar: "))
        dato = [c for c in dato if c["id"] != eliminar]
        print("Contacto eliminado.")
    else:
        print("opcion no valida")
        return


    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(dato, f, indent=4, ensure_ascii=False)
    print("cambios guardados")
