import numpy as np
from shapely.geometry import LineString, Polygon, Point


def calcular_centro_trapecio(trapecio):
    # Calcula el centro del trapecio a partir de una lista que definen sus puntos
    centro = Polygon(trapecio).centroid.coords[0]
    return centro


def calcular_centro_segmento(segmentos):
    # Calcula el centro de un segmento o de un conjunto de segmentos agrupados en listas anidadas
    centros = []
    for segmento in segmentos:
        centro = LineString(segmento).centroid.coords[0]
        centros.extend([centro])
    return centros


def seleccionar_puntos(trapecio, puntos):
    # Escoje de una lista dada de puntos solamente aquellos que estén sobre las aristas del trapecio
    puntos_trapecio = []
    if len(trapecio) == 4:
        segmento_izquierda = [trapecio[1], trapecio[2]]
        segmento_derecha = [trapecio[0], trapecio[3]]
    else:
        segmento_izquierda = [trapecio[0], trapecio[2]]
        segmento_derecha = [trapecio[1], trapecio[2]]

    for punto in puntos:
        if LineString(segmento_izquierda).contains(Point(punto)) or \
           LineString(segmento_derecha).contains(Point(punto)):

            puntos_trapecio.extend([punto])

    return puntos_trapecio


def punto_en_trapecio(trapecio, punto):
    # Determina si el punto suministrado se encuentra en el interior del trapecio
    return Polygon(trapecio).contains(Point(punto))


class RoadMap:
    def __init__(self, trapecios, lineas_divisorias, fronteras_trapecios, fronteras_compartidas, start, meta):
        # Contendrá una lista de todos los trapecios y de las líneas de división generadas por el Algoritmo de
        # Trapezoidación
        self.trapecios = None
        self.lineas_divisorias = None

        # Contendrá las listas de las fronteras laterales de cada trapecio
        self.fronteras_trapecios = None

        # Contendrá un diccionario con las fronteras comunes a cada trapecio
        self.fronteras_compartidas = None

        # Variables que almacenarán los centros de los trapecios y de las rectas verticales que los separan
        self.centros_trapecios = None
        self.centros_lineas = None

        # Almacenarán las coordenadas (x, y) del Start y la Meta
        self.coordenadas_start = None
        self.coordenadas_meta = None

        # Variables que almacenarán los índices de los trapecios que contengan los puntos de Start y Meta
        self.start = None
        self.meta = None

        # Lista que contendrá los puntos de conexión para cada trapecio
        self.puntos_conexion = None

        # Variables del Algoritmo de Dijkstra
        self.lista = None
        self.distancias = None
        self.padres = None

        # Configuración inicial de la técnica de roadmap
        self.configurar(trapecios, lineas_divisorias, fronteras_trapecios, fronteras_compartidas, start, meta)

    def configurar(self, trapecios, lineas_divisorias, fronteras_trapecios, fronteras_compartidas, start, meta):
        # Inicializando la lista de trapecios
        self.trapecios = trapecios

        # Inicializando la lista de líneas divisorias
        self.lineas_divisorias = lineas_divisorias

        # Inicializando las listas que almacenarán los centros de los trapecios y de cada segmento que conforman
        # las líneas verticales
        self.centros_trapecios = []
        self.centros_lineas = []

        # Inicializando las fronteras laterales de los trapecios
        self.fronteras_trapecios = fronteras_trapecios

        # Inicializando las fronteras compartidas por cada trapecio
        self.fronteras_compartidas = fronteras_compartidas

        # Inicializando las coordenadas del Start y la Meta
        self.coordenadas_start = start
        self.coordenadas_meta = meta

        # Creando una lista vacía que almacenará los puntos de conexión para cada trapecio
        self.puntos_conexion = []

        # Variables para el Algoritmo de Dijkstra
        self.lista = []
        self.distancias = np.full(len(self.trapecios), np.inf)
        self.padres = np.empty(len(self.trapecios), dtype=object)

        # Realizando los ajustes iniciales
        self.ajuste_inicial()

    def ajuste_inicial(self):
        # Determinando los centros de los trapecios y la ubicación de los puntos de Start y Meta
        for indice, trapecio in enumerate(self.trapecios, 0):
            self.centros_trapecios.append(calcular_centro_trapecio(trapecio))
            # Ubicación de los puntos de Start y Meta
            if punto_en_trapecio(trapecio, self.coordenadas_start):
                self.start = indice
            if punto_en_trapecio(trapecio, self.coordenadas_meta):
                self.meta = indice

        # Estableciendo la distancia para el Start
        self.distancias[self.start] = 0
        # Añadiendo el Start a la lista
        self.lista.append(self.start)
        # Estableciendo como padre del nodo Start su mismo nodo
        self.padres[self.start] = self.start

        # Determinando los centros de los segmentos que conforman las líneas divisorias
        for puntos in self.lineas_divisorias:
            segmentos = []
            # Formando segmentos
            if len(puntos) == 3:
                if puntos[0] != puntos[1]:
                    segmento1 = [puntos[0], puntos[1]]
                    segmento2 = [puntos[1], puntos[2]]
                    segmentos.extend([segmento1, segmento2])
                else:
                    segmento2 = [puntos[1], puntos[2]]
                    segmentos.extend([segmento2])

            elif len(puntos) == 2:
                if puntos[0] != puntos[1]:
                    segmentos.extend([puntos])

            self.centros_lineas.append(calcular_centro_segmento(segmentos))

    def ejecutar(self):
        finalizacion_satisfactoria = False
        while self.lista:
            # Buscando nodo en la lista con la menor distancia
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

            # Buscando nodos vecinos
            vecinos_izquierda, vecinos_derecha = self.buscar_nodos_vecinos(nodo_actual)

            if vecinos_izquierda is not None:
                for vecino in vecinos_izquierda:
                    # Distancia del nodo nodo actual al vecino
                    distancia_al_vecino = self.calcular_distancia(nodo_actual, vecino, "izquierdo")
                    if self.distancias[vecino] > self.distancias[nodo_actual] + distancia_al_vecino:
                        self.distancias[vecino] = self.distancias[nodo_actual] + distancia_al_vecino
                        self.padres[vecino] = nodo_actual

                        # Añadiendo el nodo a la lista si no está en ella
                        if vecino not in self.lista:
                            self.lista.append(vecino)

            if vecinos_derecha is not None:
                for vecino in vecinos_derecha:
                    # Distancia del nodo nodo actual al vecino
                    distancia_al_vecino = self.calcular_distancia(nodo_actual, vecino, "derecho")
                    if self.distancias[vecino] > self.distancias[nodo_actual] + distancia_al_vecino:
                        self.distancias[vecino] = self.distancias[nodo_actual] + distancia_al_vecino
                        self.padres[vecino] = nodo_actual

                        # Añadiendo el nodo a la lista si no está en ella
                        if vecino not in self.lista:
                            self.lista.append(vecino)

        # Devolviendo los resultados
        centros_trapecios = self.obtener_centros_trapecios()
        centros_lineas = self.obtener_centros_lineas()
        if finalizacion_satisfactoria:
            nodos_trayectoria = self.obtener_nodos_trayectoria()
            puntos_trayectoria = self.puntos_trayectoria(nodos_trayectoria)
        else:
            nodos_trayectoria = None
            puntos_trayectoria = None
        return [centros_trapecios, centros_lineas, nodos_trayectoria, puntos_trayectoria]

    def buscar_nodos_vecinos(self, nodo_actual):
        # nodo_actual es igual al índice del trapecio
        if len(self.fronteras_trapecios[nodo_actual]) == 2:
            limite_izquierdo, limite_derecho = self.fronteras_trapecios[nodo_actual]

            # Analizando los puntos del límite izquierdo
            puntos = self.lineas_divisorias[limite_izquierdo]
            if len(puntos) == 1:
                limite_izquierdo = None
            elif len(puntos) == 2:
                if puntos[0] == puntos[1]:
                    limite_izquierdo = None

            # Analizando los puntos del límite derecho
            puntos = self.lineas_divisorias[limite_derecho]
            if len(puntos) == 1:
                limite_derecho = None
            elif len(puntos) == 2:
                if puntos[0] == puntos[1]:
                    limite_derecho = None
        else:
            limite_izquierdo = self.fronteras_trapecios[nodo_actual][0]
            limite_derecho = None

        # Buscando vecinos del límite izquierdo del nodo actual
        vecinos_izquierda = []
        if limite_izquierdo is not None:
            for vecino in self.fronteras_compartidas[str(limite_izquierdo)]:
                if self.trapecios[nodo_actual] != self.trapecios[vecino]:
                    if len(self.fronteras_trapecios[vecino]) == 2:
                        if limite_izquierdo == self.fronteras_trapecios[vecino][1]:
                            vecinos_izquierda.append(vecino)

        # Buscando vecinos del límite derecho del nodo actual
        vecinos_derecha = []
        if limite_derecho is not None:
            for vecino in self.fronteras_compartidas[str(limite_derecho)]:
                if self.trapecios[nodo_actual] != self.fronteras_trapecios[vecino]:
                    if limite_derecho == self.fronteras_trapecios[vecino][0]:
                        vecinos_derecha.append(vecino)

        # Si las listas están vacías, se establecen en None
        if not vecinos_izquierda:
            vecinos_izquierda = None
        if not vecinos_derecha:
            vecinos_derecha = None

        return vecinos_izquierda, vecinos_derecha

    def calcular_distancia(self, nodo_actual, nodo_vecino, lado_vecino):
        centro_nodo_actual = self.centros_trapecios[nodo_actual]
        centro_nodo_vecino = self.centros_trapecios[nodo_vecino]

        # Encontrando los puntos de conexión
        if lado_vecino == "izquierdo":
            limite_izquierdo_nodo_actual = self.fronteras_trapecios[nodo_actual][0]
            limite_derecho_vecino = self.fronteras_trapecios[nodo_vecino][1]

            puntos_nodo_actual = seleccionar_puntos(self.trapecios[nodo_actual],
                                                    self.centros_lineas[limite_izquierdo_nodo_actual])
            puntos_vecino = seleccionar_puntos(self.trapecios[nodo_vecino],
                                               self.centros_lineas[limite_derecho_vecino])
        # Lado derecho
        else:
            limite_derecho_nodo_actual = self.fronteras_trapecios[nodo_actual][1]
            limite_izquierdo_vecino = self.fronteras_trapecios[nodo_vecino][0]

            puntos_nodo_actual = seleccionar_puntos(self.trapecios[nodo_actual],
                                                    self.centros_lineas[limite_derecho_nodo_actual])
            puntos_vecino = seleccionar_puntos(self.trapecios[nodo_vecino],
                                               self.centros_lineas[limite_izquierdo_vecino])

        # Estableciendo la conexión
        punto_de_conexion = None
        for punto in puntos_nodo_actual:
            if punto in puntos_vecino:
                punto_de_conexion = punto
                break

        # Calculando la distancia
        # Distancia del centro del nodo actual hasta el punto de conexión
        distancia1 = Point(centro_nodo_actual).distance(Point(punto_de_conexion))
        # Distancia del punto de conexión al centro del nodo vecino
        distancia2 = Point(punto_de_conexion).distance(Point(centro_nodo_vecino))

        distancia = distancia1 + distancia2

        return distancia

    # Devuelve las regiones trapezoidales (nodos) que constituyen la trayectoria
    def obtener_nodos_trayectoria(self):
        nodos_trayectoria = [self.meta]
        nodo_actual = self.meta
        while self.padres[nodo_actual] != nodo_actual:
            nodo_actual = self.padres[nodo_actual]
            nodos_trayectoria.insert(0, nodo_actual)

        return nodos_trayectoria

    # Devuelve los puntos que conforman la trayectoria
    def puntos_trayectoria(self, nodos_trayectoria):
        trayectoria = [self.coordenadas_start]
        for indice, nodo in enumerate(nodos_trayectoria, 0):
            centro_nodo = self.centros_trapecios[nodo]
            trayectoria.append(centro_nodo)
            if indice < len(nodos_trayectoria) - 1:
                nodo_actual = nodo
                nodo_vecino = nodos_trayectoria[indice + 1]
                punto_de_conexion = self.determinar_conexion(nodo_actual, nodo_vecino)
                trayectoria.append(punto_de_conexion)
        trayectoria.append(self.coordenadas_meta)
        return trayectoria

    def determinar_conexion(self, nodo_actual, nodo_vecino):
        fronteras_nodo_actual = self.fronteras_trapecios[nodo_actual]
        fronteras_nodo_vecino = self.fronteras_trapecios[nodo_vecino]

        # Puntos de conexión del nodo actual
        puntos_nodo_actual = []
        for frontera in fronteras_nodo_actual:
            puntos_nodo_actual += seleccionar_puntos(self.trapecios[nodo_actual],
                                                     self.centros_lineas[frontera])
        # Puntos de conexión del nodo vecino
        puntos_nodo_vecino = []
        for frontera in fronteras_nodo_vecino:
            puntos_nodo_vecino += seleccionar_puntos(self.trapecios[nodo_vecino],
                                                     self.centros_lineas[frontera])
        punto_de_conexion = None
        for punto in puntos_nodo_actual:
            if punto in puntos_nodo_vecino:
                punto_de_conexion = punto
                break

        return punto_de_conexion

    def obtener_centros_trapecios(self):
        return self.centros_trapecios

    def obtener_centros_lineas(self):
        return self.centros_lineas
