import os


def leer_fichero(ruta):
    claves = None
    try:
        # Comprueba si el archivo está vacío
        comprobacion = os.stat(ruta).st_size == 0
        if not comprobacion:
            archivo = open(ruta, "r")
            claves = []
            for linea in archivo:
                if linea != "\n":
                    clave = linea.strip()   # Elimina los espacios en blanco al inicio y al final del String
                    claves.append(clave)
            archivo.close()
    except Exception as e:
        print(e)
    return claves


# Construye un nuevo fichero, o sobreescribe todos los datos existententes en el mismo
def construir_fichero(ruta, datos):
    respuesta = False
    try:
        archivo = open(ruta, "w")
        for dato in datos:
            archivo.write(dato + "\n")
        archivo.close()
        respuesta = True
    except Exception as e:
        print(e)
    return respuesta


# Construye un nuevo fichero, o agrega datos al final de los datos existentes
def editar_fichero(ruta, datos):
    respuesta = False
    try:
        archivo = open(ruta, "a")
        for dato in datos:
            archivo.write(dato + "\n")
        archivo.close()
        respuesta = True
    except Exception as e:
        print(e)
    return respuesta


def eliminar_fichero(ruta):
    respuesta = False
    try:
        os.remove(ruta)
        respuesta = True
    except Exception as e:
        print(e)
    return respuesta
