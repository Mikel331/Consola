import os
import time
import requests
import threading
import json
from datetime import datetime

config_file = "config.json"
datos = "datos"

def guardarConfig(conf):
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)

def cargarConfig():
    if not os.path.exists(config_file):
        conf = {
            "api_url": "http://127.0.0.1:5000/getDatos",
            "recarga": 2
        }
        guardarConfig(conf)
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

config = cargarConfig()
os.makedirs(datos, exist_ok=True)

def descargarDatos():
    ultimoArchivo = None
    while True:
        try:
            print("\nDescargando datos...")
            r = requests.get(config["api_url"], timeout=10)
            if r.status_code == 200:
                dato = r.json()
                for contacto in dato:
                    if "image_1920" in contacto and contacto["image_1920"]:
                        img = contacto["image_1920"]
                        if len(img) > 50:
                            contacto["image_1920"] = img[:50] + "...[BASE64]"
                        else:
                            contacto["image_1920"] = img

                if dato != ultimoArchivo:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombreArchivo = os.path.join(datos, f"contactos_{timestamp}.json")
                    with open(nombreArchivo, "w", encoding="utf-8") as f:
                        json.dump(dato, f, indent=4, ensure_ascii=False)
                    ultimoArchivo = dato
                    print(f"Datos guardados en {nombreArchivo}")
                else:
                    print("No hay nuevos datos")
            else:
                print(f"Error {r.status_code}")
        except Exception as e:
            print(f"Error {e}")
        time.sleep(config["recarga"] * 60)

def mostrarFicheros():
    ficheros = sorted(os.listdir(datos))
    if not ficheros:
        print("No hay ficheros")
        return []
    print("\nFicheros disponibles:")
    for i, f in enumerate(ficheros, 1):
        print(f"{i}. {f}")
    return ficheros

def seleccionarFichero():
    ficheros = mostrarFicheros()
    if not ficheros:
        return None
    eleccion = input("\nNumero o nombre del fichero: ")
    if eleccion.isdigit():
        idx = int(eleccion) - 1
        if 0 <= idx < len(ficheros):
            return os.path.join(datos, ficheros[idx])
    elif eleccion in ficheros:
        return os.path.join(datos, eleccion)
    print("Fichero no encontrado")
    return None

def verFichero():
    ruta = seleccionarFichero()
    if ruta:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = json.load(f)
            print(json.dumps(contenido, indent=2, ensure_ascii=False))

def editarFichero():
    ruta = seleccionarFichero()
    if not ruta:
        return
    with open(ruta, "r", encoding="utf-8") as f:
        dato = json.load(f)

    print("\n1. Anadir contacto")
    print("2. Modificar contacto")
    print("3. Eliminar contacto")
    op = input("Selecciona: ")

    if op == "1":
        nuevo = {}
        nuevo["id"] = int(input("ID: "))
        nuevo["name"] = input("Nombre: ")
        nuevo["email"] = input("Email: ")
        nuevo["phone"] = input("Telefono: ")
        dato.append(nuevo)
        print("Contacto anadido")

    elif op == "2":
        modificar = int(input("ID del contacto a modificar: "))
        encontrado = next((c for c in dato if c["id"] == modificar), None)
        if encontrado:
            encontrado["name"] = input(f"Nuevo nombre ({encontrado['name']}): ") or encontrado["name"]
            encontrado["email"] = input(f"Nuevo email ({encontrado['email']}): ") or encontrado["email"]
            encontrado["phone"] = input(f"Nuevo telefono ({encontrado['phone']}): ") or encontrado["phone"]
            print("Contacto actualizado")
        else:
            print("No se encontro el contacto")

    elif op == "3":
        eliminar = int(input("ID del contacto a eliminar: "))
        dato = [c for c in dato if c["id"] != eliminar]
        print("Contacto eliminado")
    else:
        print("Opcion no valida")
        return

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(dato, f, indent=4, ensure_ascii=False)
    print("Cambios guardados")

def editarConfig():
    print(f"\nConfiguracion actual:")
    print(json.dumps(config, indent=4, ensure_ascii=False))
    print("\n1. Cambiar URL de la API")
    print("2. Cambiar tiempo de descarga (minutos)")
    print("3. Salir")
    op = input("Selecciona: ")

    if op == "1":
        config["api_url"] = input("Nueva URL: ")
    elif op == "2":
        nuevo = input("Nuevo tiempo (min): ")
        if nuevo.isdigit():
            config["recarga"] = int(nuevo)
        else:
            print("Valor no valido")
    guardarConfig(config)
    print("Configuracion actualizada")

def ping_api_http():
    try:
        r = requests.get(config["api_url"], timeout=5)
        if r.status_code == 200:
            print("Servidor disponible (HTTP 200)")
        else:
            print(f"Servidor responde, pero con codigo {r.status_code}")
    except requests.RequestException as e:
        print(f"No se pudo conectar al servidor: {e}")

def menu():
    while True:
        print("\n=========== MENU PRINCIPAL ===========")
        print("1. Mostrar ficheros")
        print("2. Ver contenido de un fichero")
        print("3. Editar (añadir/modificar/eliminar) contactos en un fichero")
        print("4. Configuracion")
        print("5. Ping a la API")
        print("6. Salir")
        op = input("Selecciona una opcion: ")

        if op == "1":
            mostrarFicheros()
        elif op == "2":
            verFichero()
        elif op == "3":
            editarFichero()
        elif op == "4":
            editarConfig()
        elif op == "5":
            ping_api_http()
        elif op == "6":
            print("Saliendo del programa...")
            break
        else:
            print("Opcion no valida")

if __name__ == "__main__":
    hilo = threading.Thread(target=descargarDatos, daemon=True)
    hilo.start()
    menu()
