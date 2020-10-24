import numpy as np


class Grassfire2D:
    def __init__(self, entorno, start, meta):
        # Variables que definirán aspectos del entorno sobre el que actuará el agoritmo
        self.entorno = None
        self.start = None
        self.meta = None

        # Número de filas y columnas del entorno
        self.n_filas = None
        self.n_columnas = None

        # Variables que almacenan los nodos visitados y sus distancias respectivas
        self.lista = None
        self.distancias = None

        # Configuración inicial
        self.configurar(entorno, start, meta)

    def configurar(self, entorno, start, meta):
        # Inicializando los parámetros del entorno
        self.entorno = entorno
        self.start = start
        self.meta = meta

        # Construyendo una matriz de distancias de acuerdo con el tamaño del entorno
        self.n_filas, self.n_columnas = self.entorno.shape
        self.distancias = np.full((self.n_filas, self.n_columnas), np.inf)
        
        # Construyendo una lista vacía
        self.lista = []

        # Estableciendo el valor para la Meta
        self.distancias[self.meta] = 0
        self.lista.append(self.meta)

    def ejecutar(self):
        finalizacion_satisfactoria = False
        while self.lista:
            nodo_actual = self.lista[0]

            # Eliminando el primer elemento de la lista
            self.lista.pop(0)

            # Finaliza la ejecución del algoritmo una vez que se haya encontrado el objetivo
            if nodo_actual == self.start:
                self.lista.clear()  # Limpiando la lista
                finalizacion_satisfactoria = True
                break
            
            # Nodos adyacentes
            nodos_adyacentes = self.buscar_nodos_vecinos(nodo_actual)

            for nodo in nodos_adyacentes:
                if self.distancias[nodo] == np.inf:
                    self.distancias[nodo] = self.distancias[nodo_actual] + 1
                    self.lista.append(nodo)

        if finalizacion_satisfactoria:
            # Retornando los nodos de la trayectoria
            trayectoria = self.obtener_trayectoria()
            return trayectoria
        else:
            return None

    def buscar_nodos_vecinos(self, nodo_actual):
        nodos_vecinos = []
        probables_vecinos = [(nodo_actual[0]+1, nodo_actual[1]), (nodo_actual[0], nodo_actual[1]-1),
                             (nodo_actual[0]-1, nodo_actual[1]), (nodo_actual[0], nodo_actual[1]+1)]
        for vecino in probables_vecinos:
            condicion1 = (vecino[0] >= 0) and (vecino[0] < self.n_filas)
            condicion2 = (vecino[1] >= 0) and (vecino[1] < self.n_columnas)
            if condicion1 and condicion2:
                if self.entorno[vecino] != 1:
                    nodos_vecinos.append(vecino)

        return nodos_vecinos

    def obtener_trayectoria(self):
        trayectoria = []
        hasta = self.distancias[self.start]
        if hasta != np.inf:
            # Añadiendo el start a la trayectoria
            trayectoria.append(self.start)
            hasta = int(hasta)
            nodo_actual = self.start
            iterador = 0
            while iterador < hasta:
                nodos_vecinos = self.buscar_nodos_vecinos(nodo_actual)
                punto_actual = self.distancias[nodo_actual]
                for nodo in nodos_vecinos:
                    distancia_nodo = self.distancias[nodo]
                    if distancia_nodo == punto_actual - 1:
                        trayectoria.append(nodo)
                        nodo_actual = nodo
                        iterador += 1
                        break

        return trayectoria
