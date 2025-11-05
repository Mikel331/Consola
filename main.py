import os
import time
import requests
import threading
import json
from datetime import datetime
import base64

# se guarda la configuracion, como la url de la api y el tiempo de recarga
config_file = "config.json"
# aqui se guardan los datos de los contactos
datos = "datos"
lock = threading.Lock()  


def guardarConfig(conf):
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)

# si el archivo json de config no existe lo crea
def cargarConfig():
    if not os.path.exists(config_file):
        conf = {
            "api_url": "http://apireto1.duckdns.org/getDatos",  # url d api
            "recarga": 2  #tiempo de recarga
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
            #get a la api
            r = requests.get(config["api_url"], timeout=10)
            if r.status_code == 200:
                dato = r.json()  # convierte la respuesta en json
                for contacto in dato:
                    if "image_1920" in contacto and contacto["image_1920"]:
                        img = contacto["image_1920"]
                        contacto["image_1920"] = (img[:50] + "...[BASE64]") if len(img) > 50 else img

                # Guarda los datos solo si han cambiado desde la última descarga
                if dato != ultimoArchivo:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombreArchivo = os.path.join(datos, f"contactos_{timestamp}.json")
                    with open(nombreArchivo, "w", encoding="utf-8") as f:
                        json.dump(dato, f, indent=4, ensure_ascii=False)
                    ultimoArchivo = dato
                    with lock:
                        print(f"Datos guardados en {nombreArchivo}")
            else:
                with lock:
                    print(f"Error {r.status_code}")
        except Exception as e:
            with lock:
                print(f"Error: {e}")
        
        # espera 120 sg para volver a descargar datos
        time.sleep(config["recarga"] * 60)



def mostrarFicheros():
#Muestra los ficheros que hay en la carpeta datos
    ficheros = sorted(os.listdir(datos))
    if not ficheros:
        print("No hay ficheros")
        return []
    print("\nFicheros disponibles:")
    for i, f in enumerate(ficheros, 1):
        print(f"{i}. {f}")
    return ficheros # se imprimen

def seleccionarFichero():
    # permite seleccionar un fichero por numero o por nombre
    ficheros = mostrarFicheros()
    if not ficheros:
        return None
    eleccion = input("\nnumero o nombre del fichero: ")
    if eleccion.isdigit():
        idx = int(eleccion) - 1
        if 0 <= idx < len(ficheros):
            return os.path.join(datos, ficheros[idx])
    elif eleccion in ficheros:
        return os.path.join(datos, eleccion)
    print("Fichero no encontrado")
    return None

def verFichero():
    #muestra el contenido del fichero que se elije
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

    print("\n1. Añadir contacto")
    print("2. Modificar contacto")
    print("3. Eliminar contacto")
    op = input("Selecciona: ")

    if op == "1":
        nuevo = {
            "name": input("Nombre: "),
            "email": input("Email: "),
            "phone": input("Teléfono: ")
        }

        # Si hay imagen local
        ruta_img = input("Ruta de imagen (opcional): ")
        if ruta_img and os.path.exists(ruta_img):
            with open(ruta_img, "rb") as img_file:
                base64_img = base64.b64encode(img_file.read()).decode("utf-8")
                nuevo["image_1920"] = f"data:image/png;base64,{base64_img}"

        dato.append(nuevo)
        print("Contacto añadido")

        # llamada api para añadir contacto
        try:
            r = requests.post("http://apireto1.duckdns.org/añadirDatos", json=nuevo)
            print(f"{r.status_code}")
        except Exception as e:
            print(f"Error{e}")

    elif op == "2":
        modificar = int(input("ID del contacto a modificar: "))
        encontrado = next((c for c in dato if c["id"] == modificar), None)
        if encontrado:
            encontrado["name"] = input(f"Nuevo nombre ({encontrado['name']}): ") or encontrado["name"]
            encontrado["email"] = input(f"Nuevo email ({encontrado['email']}): ") or encontrado["email"]
            encontrado["phone"] = input(f"Nuevo teléfono ({encontrado['phone']}): ") or encontrado["phone"]

            print("Contacto actualizado")

            # llamada a la api para modificar
            try:
                r = requests.put(f"http://apireto1.duckdns.org/modificarContacto/{modificar}", json=encontrado)
                print(f"Respuesta API: {r.status_code} -> {r.text}")
            except Exception as e:
                print(f"Error {e}")
        else:
            print("No se encontro el contacto")

    elif op == "3":
        eliminar = int(input("ID del contacto a eliminar: "))
        dato = [c for c in dato if c["id"] != eliminar]
        print("Contacto eliminado")

        # llamada para eliminar
        try:
            r = requests.delete(f"http://apireto1.duckdns.org/eliminarContacto/{eliminar}")
            print(f"Respuesta API: {r.status_code} -> {r.text}")
        except Exception as e:
            print(f"Error al eliminar en la API: {e}")

    else:
        print("Opción no válida")
        return

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(dato, f, indent=4, ensure_ascii=False)
    print("Cambios guardados")



def editarConfig():
   #permite cambiar la url de la api y el tiempo de recarga
    print(f"\nconfiguracion actual:")
    print(json.dumps(config, indent=4, ensure_ascii=False))
    print("\n1. Cambiar URL de la API")
    print("2. Cambiar tiempo de descarga (minutos)")
    print("3. Salir")
    op = input("Selecciona: ")

    if op == "1":
        config["api_url"] = input("Nueva URL: ")
    elif op == "2":
        nuevo = input("Nuevo tiempo: ")
        if nuevo.isdigit():
            config["recarga"] = int(nuevo)
        else:
            print("valor no valido")
    guardarConfig(config)
    print("configuracion actualizada")



def ping_api_http():
#comprueba si la api esta disponible
    try:
        r = requests.get(config["api_url"], timeout=5)
        if r.status_code == 200:
            print("Servidor disponible")
        else:
            print(f"Error HTTP: {r.status_code}")
    except requests.RequestException as e:
        print(f"Error {e}")

#menu

def menu():
    while True:
        print("\n=========== MENU PRINCIPAL ===========")
        print("1. Mostrar ficheros")
        print("2. Ver contenido de un fichero")
        print("3. Editar contactos en un fichero")
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
            print("opcion no valida")


if __name__ == "__main__":
    hilo = threading.Thread(target=descargarDatos, daemon=True)
    hilo.start()
    menu()
