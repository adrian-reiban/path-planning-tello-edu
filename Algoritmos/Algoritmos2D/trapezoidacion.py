import bisect
from shapely.geometry import LinearRing, LineString, Point, Polygon


def ordenar_vertices(vertices, etiquetas):
    """
    Ordena los vértices de izquierda a derecha en orden creciente de la coordenada x.

    :param vertices:  Lista con los vértices de todos los obstáculos que forman el entorno.
    :param etiquetas: Lista que contiene claves numéricas que indican el vértice perteneciente a un
                      obstáculo en particular. Ejemplo: 0 (obstáculo 0), 1 (obstáculo 1), 2 (obstáculo 2), etc.
                      El número de etiquetas debe ser igual a la cantidad de vértices asignados en el parámetro.
    :return: Devuelve una lista con los vértices ordenados.
    """
    vertices_ordenados = sorted(zip(vertices, etiquetas))
    # vo_obstaculos, etiquetas_ordenadas = map(list, zip(*orden))
    return vertices_ordenados


def determinar_concavidad(vertices):
    """
    Determina la concavidad o convexidad de un vértice, basándose en el conjunto de puntos suministrados
    y la tendencia horaria o antihoraria que presenten:

    .- Sentido horario = convexo

    .- Sentido antihorario = cóncavo

    Es necesario que los puntos se especifiquen en sentido u orden natural a cómo se asignan en el polígono,
    de lo contrario la respuesta será incorrecta.

    :param vertices: Lista de puntos, donde el vértice a evaluar deberá ocupar una posición central en la lista:
                     [vértice anterior, vértice a evaluar, vértice posterior]

    :return: Devuelve True si el vértice es cóncavo, y False si es convexo.
    """
    return LinearRing(vertices).is_ccw


def determinar_tipo(poligono, vertice):
    """
    Determina el tipo de vértice, cual puede catalogarse en uno de seis tipos diferentes.

    :param poligono: Coordenadas que forman el polígono (obstáculo en el espacio). Deben estar especificadas en
                     sentido horario; caso contrario el resultado no será válido.

    :param vertice: Vértice perteneciente al polígono, y que será evaluado.

    :return: Devuelve el tipo de vértice, y una lista de los vértices implicados en dicho análisis.
    """
    numero_vertices = len(poligono)

    # Realizando un barrido horizontal de izquierda a derecha para evaluar el vértice
    indice = poligono.index(vertice)
    vertice_anterior = poligono[indice - 1]
    if indice == numero_vertices - 1:
        vertice_posterior = poligono[0]
    else:
        vertice_posterior = poligono[indice + 1]

    # Determinando la concavidad o convexidad del vértice
    concavidad = determinar_concavidad([vertice_anterior, vertice, vertice_posterior])

    # Determinando el tipo al que pertenece el vértice del polígono
    tipo_vertice = None
    # Ambos derecha
    if (vertice[0] < vertice_anterior[0]) and (vertice[0] < vertice_posterior[0]):
        if concavidad is False:
            tipo_vertice = 1
        else:
            tipo_vertice = 2
    # Ambos izquierda
    elif (vertice[0] > vertice_anterior[0]) and (vertice[0] > vertice_posterior[0]):
        if concavidad is False:
            tipo_vertice = 3
        else:
            tipo_vertice = 4
    # Uno derecha y otro izquierda
    elif (vertice[0] > vertice_anterior[0]) and (vertice[0] < vertice_posterior[0]) or \
         (vertice[0] > vertice_posterior[0]) and (vertice[0] < vertice_anterior[0]):
        if concavidad is False:
            tipo_vertice = 5
        else:
            tipo_vertice = 6

    return tipo_vertice, [vertice_anterior, vertice, vertice_posterior]


def construir_segmentos(vertices, tipo):
    """Construye segmentos de recta a partir de una lista de vértices. El sentido de la recta se determina por el
    tipo al que pertenece el vértice."""
    segmento1 = None
    segmento2 = None

    if tipo == 1:
        segmento1 = [vertices[1], vertices[2]]
        segmento2 = [vertices[1], vertices[0]]

    elif tipo == 2:
        segmento1 = [vertices[1], vertices[0]]
        segmento2 = [vertices[1], vertices[2]]

    elif tipo == 3:
        segmento1 = [vertices[0], vertices[1]]
        segmento2 = [vertices[2], vertices[1]]

    elif tipo == 4:
        segmento1 = [vertices[2], vertices[1]]
        segmento2 = [vertices[0], vertices[1]]

    elif tipo == 5 or tipo == 6:
        if (vertices[0][0] < vertices[1][0]) and (vertices[1][0] < vertices[2][0]):
            segmento1 = [vertices[0], vertices[1]]
            segmento2 = [vertices[1], vertices[2]]
        else:
            segmento1 = [vertices[2], vertices[1]]
            segmento2 = [vertices[1], vertices[0]]

    return segmento1, segmento2


def localizar_punto(puntos_interseccion, punto):
    """Devuelve el índice posicional del punto dentro de la lista puntos de intersección."""
    indice = bisect.bisect_left(puntos_interseccion, punto)
    return indice


def interseccion(linea_vertical, vertice, lista_segmentos):
    """
    Determina los puntos de intersección de la recta vertical con los segmentos o aristas de los obstáculos implicados

    :param linea_vertical: Recta de prueba que intersecta el entorno.
    :param vertice: Vértice desde el que parte el análisis para la intersección de la recta con los segmentos.
    :param lista_segmentos: Lista que contiene, en tiempo de ejecución, los segmentos de los obstáculos implicados.
    :return: Devuelve una lista de los puntos de intersección de la recta vetical con los segmentos.
    """
    intersecciones = []
    bisect.insort(intersecciones, Point(vertice).coords[0])
    for segmento in lista_segmentos:
        punto_interseccion = linea_vertical.intersection(LineString(segmento))
        if Point(vertice).equals(punto_interseccion):
            pass
        else:
            bisect.insort(intersecciones, punto_interseccion.coords[0])
    return intersecciones


def punto_en_segmento(segmento, punto):
    """
    Verifica si el punto forma parte del segmento.

    :return: Devuelve True si el punto forma parte del segmento o False si no lo es.
    """
    if punto in segmento:
        respuesta = True
    elif LineString(segmento).contains(Point(punto)):
        respuesta = True
    else:
        respuesta = False
    return respuesta


class Trapezoidacion:
    def __init__(self, limites_entorno, obstaculos):
        # Variables que almacenarán los datos, según las siguientes descripciones:

        # Límites del entorno
        self.limites_entorno = None

        # Contendrá las coordenas de cada ostáculo en el entorno
        self.obstaculos = None

        # Vértices ordenados del espacio poligonal
        self.vo_espacio = None

        # Vértices ordenados de todos los obstáculos del entorno
        self.vo_obstaculos = None

        # Segmentos o aristas de cada uno de los obstáculos
        self.segmentos = None

        # Líneas que separan verticalmente los trapecios del entorno
        self.lineas_divisorias = None

        # Trapecios
        self.trapecios = None

        # Contendrá, de forma posicional, una lista con los índices de las líneas divisorias
        # que forman parte de los límites laterales (izquierdo y derecho) de cada trapecio del entorno
        self.fronteras_trapecios = []

        # Contendrá para cada línea divisoria una lista de todos los trapecios que compartan dicha línea
        self.fronteras_compartidas = {}

        # Configuración inicial del algoritmo de trapezoidación
        self.configurar(limites_entorno, obstaculos)

    def configurar(self, limites_entorno, obstaculos):
        """
        Configuración inicial del algoritmo de trapezoidación.

        :param limites_entorno: Lista con las coordenadas del entorno
        :param obstaculos: Lista anidada con las coordenadas de cáda uno de los obstáculos.
        """

        self.limites_entorno = limites_entorno
        self.obstaculos = obstaculos

        # Agrupando y etiquetando los vértices de cada uno de los obstáculos del entorno
        # El tamaño de la lista será: dimension = número de obstáculos * número de aristas de cada obstáculo
        conjunto_vertices = []
        etiquetas_vertices = []
        for indice, obstaculo in enumerate(self.obstaculos, 0):
            etiquetas_vertices += [indice] * len(obstaculo)
            conjunto_vertices += obstaculo

        # Ordenando los vértices del espacio poligonal
        self.vo_espacio = sorted(self.limites_entorno)

        # Ordenando los vértices de cada uno de los obstáculos en el entorno
        self.vo_obstaculos = ordenar_vertices(conjunto_vertices, etiquetas_vertices)

        # Insertando los segmentos principales de recta en la lista de segmentos definida en el constructor
        segmento1 = [self.vo_espacio[1], self.vo_espacio[3]]
        segmento2 = [self.vo_espacio[0], self.vo_espacio[2]]
        self.segmentos = [segmento1, segmento2]

        # Inicializando la lista que contendrá las lineas_divisorias que separarán cada uno de los trapecios
        self.lineas_divisorias = []

        # Inicializando la lista que contendrá los trapecios
        self.trapecios = []

    def ejecutar(self):
        """Ejecuta el algoritmo de trapezoidación"""
        # Límite superior e inferior del entorno poligonal
        ymin, ymax = self.obtener_limites_entorno()[1]

        # Agregando los puntos superior derecho e inferior derecho del espacio a la lista de líneas divisorias
        self.lineas_divisorias = [[self.vo_espacio[1], self.vo_espacio[0]]]

        for vertice, indice_obstaculo in self.vo_obstaculos:
            linea_vertical = LineString([(vertice[0], ymax), (vertice[0], ymin)])

            obstaculo = self.obstaculos[indice_obstaculo]
            tipo, vertices_adyacentes = determinar_tipo(obstaculo, vertice)
            segmento1, segmento2 = construir_segmentos(vertices_adyacentes, tipo)

            # Tomando acciones de acuerdo al tipo de vértice
            if tipo == 1:
                # Obteniendo los puntos de intersección de la línea vertical con cada segmento presente en el entorno
                puntos_interseccion = interseccion(linea_vertical, vertice, self.segmentos)
                # Localizando el índice del vértice dentro de los puntos de intersección
                indice = localizar_punto(puntos_interseccion, Point(vertice).coords[0])

                # Construyendo la línea divisoria
                if indice == len(puntos_interseccion) - 1:
                    punto_superior = puntos_interseccion[indice]
                    punto_inferior = puntos_interseccion[indice - 1]
                elif indice == 0:
                    punto_superior = puntos_interseccion[indice + 1]
                    punto_inferior = puntos_interseccion[indice]
                else:
                    punto_superior = puntos_interseccion[indice + 1]
                    punto_inferior = puntos_interseccion[indice - 1]

                self.lineas_divisorias.append([punto_superior, vertice, punto_inferior])
                # Construyendo el trapecio
                self.construir_trapecio(self.lineas_divisorias, tipo)
                # Agregando los segmentos a la lista
                self.segmentos.extend([segmento1, segmento2])

            elif tipo == 2:
                # Agregando los segmentos a la lista
                self.segmentos.extend([segmento1, segmento2])
                # Construyendo la línea divisoria con el único punto donde intercepta la línea vertical
                self.lineas_divisorias.append([vertice])

            elif tipo == 3:
                # Removiendo los segmentos de la lista
                self.remover_segmento([segmento1, segmento2])

                # Obteniendo los puntos de intersección de la línea vertical con cada segmento presente en el entorno
                puntos_interseccion = interseccion(linea_vertical, vertice, self.segmentos)
                # Localizando el índice del vértice dentro de los puntos de intersección
                indice = localizar_punto(puntos_interseccion, Point(vertice).coords[0])

                # Construyendo la línea divisoria
                if indice == len(puntos_interseccion) - 1:
                    punto_superior = puntos_interseccion[indice]
                    punto_inferior = puntos_interseccion[indice - 1]
                elif indice == 0:
                    punto_superior = puntos_interseccion[indice + 1]
                    punto_inferior = puntos_interseccion[indice]
                else:
                    punto_superior = puntos_interseccion[indice + 1]
                    punto_inferior = puntos_interseccion[indice - 1]

                self.lineas_divisorias.append([punto_superior, vertice, punto_inferior])
                # Construyendo el trapecio
                self.construir_trapecio(self.lineas_divisorias, tipo, [segmento1, segmento2])

            elif tipo == 4:
                # Removiendo los segmentos de la lista
                self.remover_segmento([segmento1, segmento2])

                # Construyendo el trapecio
                self.construir_trapecio(self.lineas_divisorias, tipo, [segmento1, segmento2])

            elif tipo == 5 or tipo == 6:
                # Removiendo los segmentos de la lista
                self.agregar_remover([segmento1, segmento2])

                # Obteniendo los puntos de intersección de la línea vertical con cada segmento presente en el entorno
                puntos_interseccion = interseccion(linea_vertical, vertice, self.segmentos)
                # Localizando el índice del vértice dentro de los puntos de intersección
                indice = localizar_punto(puntos_interseccion, Point(vertice).coords[0])

                # Determinando la posición del vértice para establecer el punto superior e inferior de la línea
                # divisoria
                if (vertices_adyacentes[0][0] < vertices_adyacentes[1][0]) and \
                   (vertices_adyacentes[1][0] < vertices_adyacentes[2][0]):

                    if indice < len(puntos_interseccion) - 1:
                        punto_superior = puntos_interseccion[indice + 1]
                        punto_inferior = puntos_interseccion[indice]
                        self.lineas_divisorias.append([punto_superior, punto_inferior])

                        # Construyendo el trapecio
                        self.construir_trapecio(self.lineas_divisorias, tipo, [segmento1, segmento2],
                                                vertices_adyacentes)
                    else:
                        self.lineas_divisorias.append([vertice, vertice])
                        # Construyendo el trapecio
                        self.construir_trapecio(self.lineas_divisorias, tipo, [segmento1, segmento2],
                                                vertices_adyacentes)
                else:
                    if indice > 0:
                        punto_superior = puntos_interseccion[indice]
                        punto_inferior = puntos_interseccion[indice - 1]
                        self.lineas_divisorias.append([punto_superior, punto_inferior])

                        # Construyendo el trapecio
                        self.construir_trapecio(self.lineas_divisorias, tipo, [segmento1, segmento2],
                                                vertices_adyacentes)
                    else:
                        self.lineas_divisorias.append([vertice, vertice])
                        # Construyendo el trapecio
                        self.construir_trapecio(self.lineas_divisorias, tipo, [segmento1, segmento2],
                                                vertices_adyacentes)

        # Construyendo el último trapecio que completará el algoritmo de trapezoidación
        self.lineas_divisorias.append([self.vo_espacio[3], self.vo_espacio[2]])
        self.construir_trapecio(self.lineas_divisorias, None)

    def remover_segmento(self, segmentos):
        """
        Remueve segmentos de recta en la lista principal de segmentos.

        :param segmentos: Lista que contiene los segmentos que serán removidos de la lista principal.
        """
        for segmento in segmentos:
            self.segmentos.remove(segmento)

    def agregar_remover(self, segmentos):
        """
        Remueve y agrega segmentos de recta en la lista principal de segmentos.

        :param segmentos: Lista que contiene los segmentos que serán añadidos y removidos de la lista principal.
        """
        self.segmentos.remove(segmentos[0])
        self.segmentos.append(segmentos[1])

    def buscar_segmento(self, punto):
        """Devuelve el segmento que contiene al punto especificado como parámetro"""
        s = None
        for segmento in self.segmentos:
            if punto in segmento:
                s = segmento
                break
            elif LineString(segmento).contains(Point(punto)):
                s = segmento
                break
        return s

    def agregar_a_fronteras_compartidas(self, indice, trapecio):
        """Agrega el trapecio al límite correspondiente según el índice"""
        if str(indice) not in self.fronteras_compartidas:
            self.fronteras_compartidas[str(indice)] = [trapecio]
        else:
            self.fronteras_compartidas[str(indice)].append(trapecio)

    def construir_trapecio(self, lineas_divisorias, tipo, segmentos=None, vertices=None):
        """Construye trapecios en función de las líneas divisorias y el tipo de vértice.

        .- El parámetro denominado segmentos tiene especial atención en las condiciones que evalúan los tipos 3 en
        adelante; ya que son segmentos críticos dónde se determina qué línea divisoria forma parte del segmento,
        para con ello proceder a la contrucción del trapecio.

        .- El parámetro vértices es usado para tomar una acción en la contrucción del trapecio, en función de la
        ubicación del vértice principal con respecto al entorno que lo rodea. Se usa en las condiciones del
        tipo 5 y 6.
        """
        # Construye el último trapecio de la lista
        if tipo is None:
            trapecio = []
            linea_derecha = lineas_divisorias[-1]
            linea_izquierda = lineas_divisorias[-2]

            # Índice de ubicación de la línea divisoria
            ubicacion_anterior = len(lineas_divisorias) - 2

            for punto_derecha in linea_derecha:
                segmento = self.buscar_segmento(punto_derecha)
                for punto_izquierda in linea_izquierda:
                    if punto_en_segmento(segmento, punto_izquierda):
                        if not trapecio:
                            trapecio.extend([punto_izquierda, punto_derecha])
                        else:
                            trapecio.extend([punto_derecha, punto_izquierda])
                        break

            # Añadiendo el trapecio a la lista principal de trapecios
            self.trapecios.append(trapecio)
            # Añadiendo los índices de los límites laterales (izquierdo y derecho) del trapecio
            self.fronteras_trapecios.append([ubicacion_anterior])
            # Añadiendo el trapecio a la línea respectiva
            indice_trapecio = len(self.trapecios) - 1
            self.agregar_a_fronteras_compartidas(ubicacion_anterior, indice_trapecio)

        # Construye un trapecio para el vértice de tipo 1
        elif tipo == 1:
            trapecio = []
            linea_derecha = lineas_divisorias[-1]

            # Índices de ubicación de las líneas divisorias
            ubicacion_posterior = len(lineas_divisorias) - 1
            ubicacion_anterior = ubicacion_posterior

            # Formando el trapecio
            salir = False
            for linea_izquierda in reversed(lineas_divisorias[:-1]):
                # Resta progresivamente la ubicación actual para determinar el índice correspondiente a la
                # línea vertical izquierda
                ubicacion_anterior -= 1

                for indice, punto_derecha in enumerate(linea_derecha, 0):
                    # Saltando el punto intermedio para analizar solo el punto superior e inferior de la recta
                    if indice != 1:
                        segmento = self.buscar_segmento(punto_derecha)
                        for punto_izquierda in linea_izquierda:
                            if punto_en_segmento(segmento, punto_izquierda):
                                if not trapecio:
                                    trapecio.extend([punto_izquierda, punto_derecha])
                                else:
                                    if punto_derecha in trapecio:
                                        trapecio.extend([punto_izquierda])
                                    else:
                                        trapecio.extend([punto_derecha, punto_izquierda])
                                break
                        if not trapecio:
                            break
                    if len(trapecio) >= 3:
                        salir = True
                        break
                if salir is True:
                    break

            # Añadiendo el trapecio a la lista principal de trapecios
            self.trapecios.append(trapecio)
            # Añadiendo los índices de los límites laterales (izquierdo y derecho) del trapecio
            self.fronteras_trapecios.append([ubicacion_anterior, ubicacion_posterior])
            # Añadiendo el trapecio a las líneas respectivas
            indice_trapecio = len(self.trapecios) - 1
            self.agregar_a_fronteras_compartidas(ubicacion_anterior, indice_trapecio)
            self.agregar_a_fronteras_compartidas(ubicacion_posterior, indice_trapecio)

        # Construye dos trapecios para el vértice de tipo 3
        elif tipo == 3:
            trapecio1 = []
            trapecio2 = []
            segmento1 = segmentos[0]
            segmento2 = segmentos[1]
            linea_derecha = lineas_divisorias[-1]

            # Índices de ubicación de las líneas verticales
            ubicacion_posterior = len(lineas_divisorias) - 1
            ubicacion_anterior = ubicacion_posterior

            # Formando el primer trapecio
            salir = False
            for linea_izquierda in reversed(lineas_divisorias[:-1]):
                # Resta progresivamente la ubicación actual para determinar el índice correspondiente a la
                # línea vertical izquierda
                ubicacion_anterior -= 1

                for iterador in range(2):
                    if len(linea_derecha) == 3:
                        if iterador == 0:
                            punto_derecha = linea_derecha[0]
                            segmento = self.buscar_segmento(punto_derecha)
                        else:
                            punto_derecha = linea_derecha[1]
                            segmento = segmento1
                    else:
                        punto_derecha = linea_derecha[0]
                        if iterador == 0:
                            segmento = self.buscar_segmento(punto_derecha)
                        else:
                            segmento = segmento1

                    for punto_izquierda in linea_izquierda:
                        if punto_en_segmento(segmento, punto_izquierda):
                            if not trapecio1:
                                trapecio1.extend([punto_izquierda, punto_derecha])
                            else:
                                if punto_derecha in trapecio1:
                                    trapecio1.extend([punto_izquierda])
                                else:
                                    trapecio1.extend([punto_derecha, punto_izquierda])
                            break
                    if not trapecio1:
                        break
                    elif len(trapecio1) >= 3:
                        salir = True
                        break
                if salir is True:
                    break

            # Añadiendo el trapecio a la lista principal de trapecios
            self.trapecios.append(trapecio1)
            # Añadiendo los índices de los límites laterales (izquierdo y derecho) del trapecio
            self.fronteras_trapecios.append([ubicacion_anterior, ubicacion_posterior])
            # Añadiendo el trapecio a las líneas respectivas
            indice_trapecio1 = len(self.trapecios) - 1
            self.agregar_a_fronteras_compartidas(ubicacion_anterior, indice_trapecio1)
            self.agregar_a_fronteras_compartidas(ubicacion_posterior, indice_trapecio1)

            # Formando el segundo trapecio
            ubicacion_anterior = ubicacion_posterior
            salir = False
            for linea_izquierda in reversed(lineas_divisorias[:-1]):
                # Resta progresivamente la ubicación actual para determinar el índice correspondiente a la
                # línea vertical izquierda
                ubicacion_anterior -= 1

                for iterador in range(2):
                    if len(linea_derecha) == 3:
                        if iterador == 0:
                            punto_derecha = linea_derecha[1]
                            segmento = segmento2
                        else:
                            punto_derecha = linea_derecha[2]
                            segmento = self.buscar_segmento(punto_derecha)
                    else:
                        if iterador == 0:
                            punto_derecha = linea_derecha[0]
                            segmento = segmento2
                        else:
                            punto_derecha = linea_derecha[1]
                            segmento = self.buscar_segmento(punto_derecha)

                    for punto_izquierda in linea_izquierda:
                        if punto_en_segmento(segmento, punto_izquierda):
                            if not trapecio2:
                                trapecio2.extend([punto_izquierda, punto_derecha])
                            else:
                                if punto_derecha in trapecio2:
                                    trapecio2.extend([punto_izquierda])
                                else:
                                    trapecio2.extend([punto_derecha, punto_izquierda])
                            break
                    if not trapecio2:
                        break
                    elif len(trapecio2) >= 3:
                        salir = True
                        break
                if salir is True:
                    break

            # Añadiendo el trapecio a la lista principal de trapecios
            self.trapecios.append(trapecio2)
            # Añadiendo los índices de los límites laterales (izquierdo y derecho) del trapecio
            self.fronteras_trapecios.append([ubicacion_anterior, ubicacion_posterior])
            # Añadiendo el trapecio a las líneas respectivas
            indice_trapecio2 = len(self.trapecios) - 1
            self.agregar_a_fronteras_compartidas(ubicacion_anterior, indice_trapecio2)
            self.agregar_a_fronteras_compartidas(ubicacion_posterior, indice_trapecio2)

        # Construye un trapecio para el vértice de tipo 4
        elif tipo == 4:
            trapecio = []
            segmento1 = segmentos[0]
            segmento2 = segmentos[1]
            punto_derecha = segmento1[1]

            # Índice de ubicación de la línea divisoria
            ubicacion_anterior = len(lineas_divisorias)

            # Formando el trapecio
            for linea_izquierda in reversed(lineas_divisorias):
                # Resta progresivamente la ubicación actual para determinar el índice correspondiente a la
                # línea vertical izquierda
                ubicacion_anterior -= 1

                for punto_izquierda in linea_izquierda:
                    if not trapecio:
                        segmento = segmento1
                    else:
                        segmento = segmento2

                    if punto_en_segmento(segmento, punto_izquierda):
                        if not trapecio:
                            trapecio.extend([punto_izquierda, punto_derecha])
                        else:
                            trapecio.extend([punto_izquierda])
                if trapecio:
                    break

            # Añadiendo el trapecio a la lista principal
            self.trapecios.append(trapecio)
            # Añadiendo los límites laterales (izquierdo y derecho) del trapecio
            self.fronteras_trapecios.append([ubicacion_anterior])
            # Añadiendo el trapecio a la línea respectiva
            indice_trapecio = len(self.trapecios) - 1
            self.agregar_a_fronteras_compartidas(ubicacion_anterior, indice_trapecio)

        # Construye un trapecio para el vértice de tipo 5 o tipo 6
        elif tipo == 5 or tipo == 6:
            trapecio = []
            segmento1 = segmentos[0]
            vertices_adyacentes = vertices
            linea_derecha = lineas_divisorias[-1]

            # Índices de ubicación de las líneas divisorias
            ubicacion_posterior = len(lineas_divisorias) - 1
            ubicacion_anterior = ubicacion_posterior

            # Construyendo el trapecio
            salir = False
            for linea_izquierda in reversed(lineas_divisorias[:-1]):
                # Resta progresivamente la ubicación actual para determinar el índice correspondiente a la
                # línea divisoria izquierda
                ubicacion_anterior -= 1

                for indice, punto_derecha in enumerate(linea_derecha, 0):
                    if (vertices_adyacentes[0][0] < vertices_adyacentes[1][0]) and \
                            (vertices_adyacentes[1][0] < vertices_adyacentes[2][0]):
                        if indice == 0:
                            segmento = self.buscar_segmento(punto_derecha)
                        else:
                            segmento = segmento1
                    else:
                        if indice == 0:
                            segmento = segmento1
                        else:
                            segmento = self.buscar_segmento(punto_derecha)

                    for punto_izquierda in linea_izquierda:
                        if punto_en_segmento(segmento, punto_izquierda):
                            if not trapecio:
                                trapecio.extend([punto_izquierda, punto_derecha])
                            else:
                                if punto_derecha in trapecio:
                                    trapecio.extend([punto_izquierda])
                                else:
                                    trapecio.extend([punto_derecha, punto_izquierda])
                            break
                    if not trapecio:
                        break
                    elif len(trapecio) >= 3:
                        salir = True
                if salir is True:
                    break

            # Añadiendo el trapecio a la lista principal
            self.trapecios.append(trapecio)
            # Añadiendo los límites laterales (izquierdo y derecho) del trapecio
            self.fronteras_trapecios.append([ubicacion_anterior, ubicacion_posterior])
            # Agregando el trapecio a las líneas divisorias correspondientes
            indice_trapecio = len(self.trapecios) - 1
            self.agregar_a_fronteras_compartidas(ubicacion_anterior, indice_trapecio)
            self.agregar_a_fronteras_compartidas(ubicacion_posterior, indice_trapecio)

    def obtener_resultados(self):
        limites_entorno = self.obtener_limites_entorno()
        lineas_divisorias = self.obtener_lineas_divisorias()
        trapecios = self.obtener_trapecios()
        fronteras_trapecios = self.obtener_fronteras_trapecios()
        fronteras_compartidas = self.obtener_fronteras_compartidas()
        return [limites_entorno, lineas_divisorias, trapecios, fronteras_trapecios, fronteras_compartidas]

    def obtener_limites_entorno(self):
        """Devuelve una lista con los límites del espacio poligonal."""
        xmin, ymin, xmax, ymax = Polygon(self.limites_entorno).bounds
        return [(xmin, xmax), (ymin, ymax)]

    def obtener_lineas_divisorias(self):
        """Devuelve una lista de las lineas_divisorias que interceptan los vértices de cada elemento dentro del
        entorno."""
        return self.lineas_divisorias

    def obtener_trapecios(self):
        """Devuelve una lista con todos los trapecios creados en el programa de trapezoidación."""
        return self.trapecios

    def obtener_fronteras_trapecios(self):
        """Devuelve una lista con los índices de las líneas divisorias que forman parte de los límites laterales
        (fronteras) de cada uno de los trapecios."""
        return self.fronteras_trapecios

    def obtener_fronteras_compartidas(self):
        """Devuelve un diccionario en el que cada clave corresponde al índice de cada línea divisoria; y su respectivo
        valor contiene una lista de todos los trapecios que comparten dicha línea.

        Nota: Los trapecios están representados por índices numéricos, que son las posiciones que ocupan dentro de la
        lista principal de trapecios.
        """
        return self.fronteras_compartidas
