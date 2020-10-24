import numpy as np


class Dijkstra2D:
    def __init__(self, entorno, start, meta):
        # Variables que definirán aspectos del entorno sobre el que actuará el agoritmo
        self.entorno = None
        self.start = None
        self.meta = None

        # Número de filas y columnas del entorno
        self.n_filas = None
        self.n_columnas = None

        # Variables que almacenarán los nodos visitados y sus distancias respectivas
        self.lista = None
        self.vertices = None
        self.distancias = None

        # Contendrá a los nodos padre de cada vértice del grafo
        self.padres = None

        # Configuración inicial
        self.configurar(entorno, start, meta)

    def configurar(self, entorno, start, meta):
        # Inicializando los parámetros del entorno
        self.entorno = entorno
        self.start = start
        self.meta = meta

        # Creando un conjunto de vértices o nodos de acuerdo con la estructura del entorno
        self.n_filas, self.n_columnas = entorno.shape
        self.vertices = np.fromfunction(lambda i, j: i + j, (self.n_filas, self.n_columnas), dtype=np.int)

        # Matriz que almacenará la distancia de cada vértice en el grafo, con respecto al nodo Start
        self.distancias = np.full((self.n_filas, self.n_columnas), np.inf)

        # Matriz que albergará los nodos padre de cada vértice en el grafo
        self.padres = np.empty((self.n_filas, self.n_columnas), dtype=object)

        # Creando una lista vacía
        self.lista = []

        # Colocando en cero la distancia para el nodo Start
        self.distancias[self.start] = 0

        # Añadiendo el nodo start a la lista
        self.lista.append(self.start)

        # Estableciendo como padre del vértice Start su mismo nodo
        self.padres[self.start] = self.start

    def ejecutar(self):
        finalizacion_satisfactoria = False
        while self.lista:
            # Buscando nodo con distancia mínima dentro de la lista
            nodo_actual = self.lista[0]

            distancia = self.distancias[nodo_actual]
            for nodo in self.lista:
                if self.distancias[nodo] < distancia:
                    nodo_actual = nodo
                    distancia = self.distancias[nodo_actual]

            # Removiendo nodo actual de la lista
            self.lista.remove(nodo_actual)

            # Finaliza la ejecución del algoritmo una vez que se haya encontrado el objetivo
            if nodo_actual == self.meta:
                self.lista.clear()  # Limpiando la lista
                finalizacion_satisfactoria = True
                break

            # Obteniendo los vecinos del nodo actual
            nodos_vecinos = self.buscar_nodos_vecinos(nodo_actual)

            for nodo in nodos_vecinos:
                distancia_actual = self.distancias[nodo_actual]
                longitud_arista = abs(self.vertices[nodo] - self.vertices[nodo_actual])
                if self.distancias[nodo] > (distancia_actual + longitud_arista):
                    self.distancias[nodo] = distancia_actual + longitud_arista
                    self.padres[nodo] = nodo_actual

                    # Añadiendo el nodo a la lista si no está en ella
                    if nodo not in self.lista:
                        self.lista.append(nodo)

        if finalizacion_satisfactoria:
            # Retornando los nodos de la trayectoria
            trayectoria = self.obtener_trayectoria()
            return trayectoria
        else:
            return None

    def buscar_nodos_vecinos(self, nodo_actual):
        nodos_vecinos = []
        probables_vecinos = [(nodo_actual[0] + 1, nodo_actual[1]), (nodo_actual[0], nodo_actual[1] - 1),
                             (nodo_actual[0] - 1, nodo_actual[1]), (nodo_actual[0], nodo_actual[1] + 1)]
        for vecino in probables_vecinos:
            condicion1 = (vecino[0] >= 0) and (vecino[0] < self.n_filas)
            condicion2 = (vecino[1] >= 0) and (vecino[1] < self.n_columnas)
            if condicion1 and condicion2:
                if self.entorno[vecino] != 1:
                    nodos_vecinos.append(vecino)

        return nodos_vecinos

    def obtener_trayectoria(self):
        trayectoria = [self.meta]
        nodo_actual = self.meta
        while self.padres[nodo_actual] != nodo_actual:
            nodo_actual = self.padres[nodo_actual]
            trayectoria.insert(0, nodo_actual)

        return trayectoria
