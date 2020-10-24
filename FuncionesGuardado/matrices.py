import os
import numpy as np


def crear_directorio(ruta):
    respuesta = False
    try:
        os.mkdir(ruta)
        respuesta = True
    except Exception as e:
        print(e)
    return respuesta


def guardar_matriz(matriz, ruta):
    respuesta = None
    try:
        # Guardando la matriz en un archivo de datos binarios
        np.save(ruta, matriz)
        respuesta = True
    except Exception as e:
        print(e)

    return respuesta


def leer_matriz(ruta):
    matriz = None
    try:
        matriz = np.load(ruta, allow_pickle=True)
    except Exception as e:
        print(e)
    return matriz
