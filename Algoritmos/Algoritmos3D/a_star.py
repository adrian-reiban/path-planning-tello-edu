import numpy as np


class AStar3D:
    def __init__(self, entorno, start, meta, numero_separadores):
        # Variables que definen el entorno sobre el que actuará el algoritmo
        self.entorno = None
        self.start = None
        self.meta = None
        self.numero_separadores = numero_separadores

        # Número de filas, columnas y niveles del entorno tridimensional
        self.n_filas = None
        self.n_columnas = None
        self.n_niveles = None

        # Variables que almacenarán los nodos visitados y sus distancias respectivas
        self.lista = None
        self.vertices = None
        self.f = None
        self.g = None

        # Almacenará los nodos padre de cada vértice del grafo tridimensional
        self.padres = None

        # Realizando los ajustes iniciales
        self.configurar(entorno, start, meta)

    def configurar(self, entorno, start, meta):
        # Inicializando parámetros del espacio tridimensional
        self.entorno = entorno
        self.start = start
        self.meta = meta

        # Creando un conjunto de vértices o nodos de acuerdo con la estructura del espacio tridimensional
        self.n_filas, self.n_columnas, self.n_niveles = entorno.shape
        self.vertices = np.fromfunction(lambda i, j, k: i + j + k,
                                        (self.n_filas, self.n_columnas, self.n_niveles), dtype=np.int)

        """Configuración de la heurística"""
        # Matrices de costo
        self.f = np.full((self.n_filas, self.n_columnas, self.n_niveles), np.inf)
        self.g = np.full((self.n_filas, self.n_columnas, self.n_niveles), np.inf)

        # Matriz que albergará los nodos padre de cada vértice en el grafo tridimensional
        self.padres = np.empty((self.n_filas, self.n_columnas, self.n_niveles), dtype=object)

        # Creando una lista vacía
        self.lista = []

        # Colocando en cero el costo para el nodo Start
        self.g[self.start] = 0
        # Costo de movimiento del nodo Start con respecto a la Meta
        self.f[self.start] = self.distancia_manhattan(self.start)

        # Añadiendo el nodo Start a la lista
        self.lista.append(self.start)

        # Estableciendo como padre del vértice start su mismo nodo
        self.padres[self.start] = self.start

    def ejecutar(self):
        finalizacion_satisfactoria = False
        while self.lista:
            # Buscando nodo con distancia mínima dentro de la lista
            nodo_actual = self.lista[0]
            distancia = self.f[nodo_actual]

            for nodo in self.lista:
                if self.f[nodo] < distancia:
                    nodo_actual = nodo
                    distancia = self.f[nodo_actual]

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
                g_nodo = self.g[nodo]
                g_actual = self.g[nodo_actual]
                longitud_arista = abs(self.vertices[nodo] - self.vertices[nodo_actual])
                if g_nodo > (g_actual + longitud_arista):
                    self.g[nodo] = g_actual + longitud_arista
                    self.f[nodo] = self.g[nodo] + self.distancia_manhattan(nodo)
                    self.padres[nodo] = nodo_actual

                    # Añadiendo el nodo a la lista si no está en ella
                    if nodo not in self.lista:
                        self.lista.append(nodo)

        if finalizacion_satisfactoria:
            trayectoria = self.obtener_trayectoria()
            return trayectoria
        else:
            return None

    def distancia_manhattan(self, nodo):
        h = abs(nodo[0] - self.meta[0]) + abs(nodo[1] - self.meta[1]) + abs(nodo[2] - self.meta[2])
        return h

    def buscar_nodos_vecinos(self, nodo_actual):
        nodos_vecinos = []
        probables_vecinos = [(nodo_actual[0] + 1, nodo_actual[1], nodo_actual[2]),
                             (nodo_actual[0], nodo_actual[1] - 1, nodo_actual[2]),
                             (nodo_actual[0] - 1, nodo_actual[1], nodo_actual[2]),
                             (nodo_actual[0], nodo_actual[1] + 1, nodo_actual[2]),
                             (nodo_actual[0], nodo_actual[1], nodo_actual[2] - 1),
                             (nodo_actual[0], nodo_actual[1], nodo_actual[2] + 1)]
        for vecino in probables_vecinos:
            condicion1 = (vecino[0] >= 0) and (vecino[0] < self.n_filas)
            condicion2 = (vecino[1] >= 0) and (vecino[1] < self.n_columnas)
            condicion3 = (vecino[2] >= 0) and (vecino[2] < self.n_niveles)

            if condicion1 and condicion2 and condicion3:
                if self.entorno[vecino]:
                    pass
                else:
                    respuesta = self.verificar_espacio(vecino)
                    if respuesta:
                        nodos_vecinos.append(vecino)

        return nodos_vecinos

    # Verifica si el nodo vecino se encuentra a una altura igual al número de voxels separadores
    # Esto permite que el drone vuele a una altura segura con respecto al obstáculo que se encuentre por debajo de él
    def verificar_espacio(self, nodo_vecino):
        respuesta = True
        for i in range(self.numero_separadores):
            nodo_espaciador = (nodo_vecino[0], nodo_vecino[1], nodo_vecino[2] - (i + 1))
            if self.entorno[nodo_espaciador]:
                respuesta = False
                break
        return respuesta

    def obtener_trayectoria(self):
        trayectoria = [self.meta]
        nodo_actual = self.meta
        while self.padres[nodo_actual] != nodo_actual:
            nodo_actual = self.padres[nodo_actual]
            trayectoria.insert(0, nodo_actual)
        return trayectoria
