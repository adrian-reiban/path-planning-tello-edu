import math
import numpy as np
import copy
from Algoritmos.Algoritmos3D.a_star import AStar3D


class AStar3DSwarm:
    def __init__(self, entorno, factor_escala, coordenadas_start, coordenadas_meta):
        # Descripción matricial del entorno 3D
        self.entorno = entorno

        # Contendrán las coordenadas Start y Meta de cada uno de los drones
        self.coordenadas_start = coordenadas_start
        self.coordenadas_meta = coordenadas_meta

        # Número de drones
        self.numero_drones = len(coordenadas_start)

        # Factor de escala
        self.factor_escala = np.array(factor_escala)

        """Restricciones de movimiento del drone impuestas por el fabricante"""
        # Nota: Todas las medidas están en metros
        # Altura de despegue mínima del drone
        self.altura_despegue = 1
        # Separacion vertical mínima entre el drone y un objeto del entorno
        self.separacion_vertical = 0.50

    def ejecutar(self):
        # Registra los drones a los que no se les pudo calcular una trayectoria única y libre de colisiones
        registro_drones = []

        # Almacena el conjunto de trayectorias calculadas para cada drone
        trayectorias_base = []
        trayectorias_simplificadas = []
        trayectorias_reales = []

        # Realizando un copia completa del entorno
        entorno_actual = copy.deepcopy(self.entorno)

        # Calculando el número de regiones o voxels hasta la altura de despegue del drone
        numero_regiones = int(math.ceil(self.altura_despegue / self.factor_escala[2]))
        # Calculando el número de voxels de separación entre el drone y un objeto del entorno
        numero_separadores = int(self.separacion_vertical / self.factor_escala[2])

        # Bloqueando los puntos de Start y Meta, así como las regiones que se encuentran sobre ellas hasta la altura de
        # despegue
        # Esto se utiliza para evitar que los drones vecinos, sobrevuelen muy cercanamente las regiones
        # de Start y Meta de los demás
        regiones_start_bloqueadas = []
        regiones_meta_bloqueadas = []
        for i in range(self.numero_drones):
            entorno_actual[self.coordenadas_start[i]] = True
            entorno_actual[self.coordenadas_meta[i]] = True

            # Regiones hasta el punto de despegue
            regiones_start = []
            regiones_meta = []
            for nivel in range(numero_regiones):
                coordenada_start = (self.coordenadas_start[i][0], self.coordenadas_start[i][1],
                                    self.coordenadas_start[i][2] + nivel + 1)
                coordenada_meta = (self.coordenadas_meta[i][0], self.coordenadas_meta[i][1],
                                   self.coordenadas_meta[i][2] + nivel + 1)

                entorno_actual[coordenada_start] = True
                entorno_actual[coordenada_meta] = True

                regiones_start.append(coordenada_start)
                regiones_meta.append(coordenada_meta)

            regiones_start_bloqueadas.append(regiones_start)
            regiones_meta_bloqueadas.append(regiones_meta)

        for drone in range(self.numero_drones):
            if drone == 0:
                # Desbloquea el punto de Start y Meta del drone actual
                entorno_actual[self.coordenadas_start[drone]] = False
                entorno_actual[self.coordenadas_meta[drone]] = False
                # Desbloqueando las regiones por encima del punto de Start y Meta
                for indice in range(numero_regiones):
                    region_start = regiones_start_bloqueadas[drone][indice]
                    region_meta = regiones_meta_bloqueadas[drone][indice]
                    entorno_actual[region_start] = False
                    entorno_actual[region_meta] = False
            else:
                # Desbloquea el punto de Start y Meta del drone actual
                entorno_actual[self.coordenadas_start[drone]] = False
                entorno_actual[self.coordenadas_meta[drone]] = False
                # Desbloqueando las regiones por encima del punto de Start y Meta
                for indice in range(numero_regiones):
                    region_start = regiones_start_bloqueadas[drone][indice]
                    region_meta = regiones_meta_bloqueadas[drone][indice]
                    entorno_actual[region_start] = False
                    entorno_actual[region_meta] = False

                # Bloquea el punto de Start y Meta del drone anterior
                entorno_actual[self.coordenadas_start[drone - 1]] = True
                entorno_actual[self.coordenadas_meta[drone - 1]] = True
                # Bloqueando las regiones por encima del punto de Start y Meta del drone anterior
                for indice in range(numero_regiones):
                    region_start = regiones_start_bloqueadas[drone - 1][indice]
                    region_meta = regiones_meta_bloqueadas[drone - 1][indice]
                    entorno_actual[region_start] = True
                    entorno_actual[region_meta] = True

            # Redefiniendo las coordenadas del Start y Meta
            start = (self.coordenadas_start[drone][0], self.coordenadas_start[drone][1],
                     self.coordenadas_start[drone][2] + numero_regiones)
            meta = (self.coordenadas_meta[drone][0], self.coordenadas_meta[drone][1],
                    self.coordenadas_meta[drone][2] + numero_separadores)
            algoritmo = AStar3D(entorno_actual, start, meta, numero_separadores)
            trayectoria = algoritmo.ejecutar()

            if trayectoria is not None:
                # Almacenando las respectivas trayectorias
                trayectoria_base, trayectoria_simplificada, trayectoria_real = ajustar_trayectoria(trayectoria,
                                                                                                   self.factor_escala,
                                                                                                   numero_regiones,
                                                                                                   numero_separadores)
                trayectorias_base.append(trayectoria_base)
                trayectorias_simplificadas.append(trayectoria_simplificada)
                trayectorias_reales.append(trayectoria_real)

                # Actualizando el entorno actual
                for punto in trayectoria:
                    entorno_actual[punto] = True
            else:
                registro_drones.append(drone + 1)

        return trayectorias_base, trayectorias_simplificadas, trayectorias_reales, registro_drones


def ajustar_trayectoria(trayectoria, factor_escala, numero_regiones, numero_separadores):
    # Ajuste de altura
    ajuste_altura = np.array([0, 0, factor_escala[2] / 2])

    # Altura de despegue
    ajuste_despegue = np.array([0, 0, numero_regiones * factor_escala[2]])

    # Definiendo un primer punto para la trayectoria
    primer_punto = (np.array((trayectoria[0]) * factor_escala) - ajuste_despegue) - ajuste_altura

    # Añadiendo el primer punto a las trayectorias
    trayectoria_base = [tuple(primer_punto)]
    trayectoria_simplificada = [tuple(primer_punto)]
    trayectoria_real = [tuple(primer_punto - ajuste_altura)]

    vector_anterior = None
    for indice in range(len(trayectoria)):
        if indice == 0:
            vector_a = np.array(trayectoria[0]) - ajuste_altura
            vector_b = np.array(trayectoria[indice])
        else:
            vector_a = np.array(trayectoria[indice - 1])
            vector_b = np.array(trayectoria[indice])

        vector = (vector_b - vector_a)

        if vector_anterior is None:
            vector_anterior = vector
        else:  # Verifica si los vectores son colineales
            producto_cruz = np.cross(vector, vector_anterior)
            if np.array_equal(producto_cruz, np.zeros(3)):
                vector_anterior = vector + vector_anterior
            else:
                trayectoria_base.append(tuple(vector_a * factor_escala))
                trayectoria_simplificada.append(tuple(vector_a * factor_escala))
                trayectoria_real.append(tuple((vector_a * factor_escala) - ajuste_altura))
                vector_anterior = vector

    # Escalando el penúltimo punto de la trayectoria
    penultimo_punto = np.array(trayectoria[-1]) * factor_escala

    # Definiendo el último punto para la trayectoria
    ultimo_punto = penultimo_punto - ajuste_altura - np.array([0, 0, numero_separadores * factor_escala[2]])

    trayectoria_base.append(tuple(penultimo_punto))
    trayectoria_simplificada.append(tuple(penultimo_punto))
    trayectoria_real.append(tuple(penultimo_punto - ajuste_altura))

    trayectoria_base.append(tuple(ultimo_punto))
    trayectoria_simplificada.append(tuple(ultimo_punto))
    trayectoria_real.append(tuple(ultimo_punto - ajuste_altura))

    return trayectoria_base, trayectoria_simplificada, trayectoria_real
