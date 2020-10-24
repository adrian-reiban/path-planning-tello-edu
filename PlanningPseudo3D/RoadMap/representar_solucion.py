"""Solución del entorno"""
from vedo import Line, Point, Points, buildAxes, show, settings, embedWindow, screenshot
# Mejores fuentes: Bongas, Comae, Kanopus, Quikhand, SmartCouric, Theemim, Normografo
settings.defaultFont = "SmartCouric"
settings.screeshotScale = 2     # Calidad de imagen, el valor debe ser un número entero
embedWindow(False)


class RepresentarSolucion:
    def __init__(self, limites_entorno, obstaculos, start, meta, trayectoria, altura_obstaculos, offset_obstaculos,
                 offset_trayectoria):

        # Límites del entorno
        self.limites_entorno = limites_entorno

        # Obstáculos del entorno
        self.obstaculos = obstaculos

        # Puntos de Start y Meta
        self.start = start
        self.meta = meta

        # Puntos de trayectoria
        self.trayectoria = trayectoria

        # Altura uniforme de los obstáculos del entorno
        self.altura = altura_obstaculos

        # Offset en Z de los obstáculos del entorno
        self.offset_obstaculos = offset_obstaculos

        # Offset en Z de los puntos de trayectoria
        self.offset_trayectoria = offset_trayectoria

        # Configuración inicial
        self.configuracion()

    def configuracion(self):
        # Transformando las coordenadas 2D de los vértices de los obstáculos a coordenadas 3D
        lista_vertices = []
        for obstaculo in self.obstaculos:
            vertices_obstaculo = []
            for punto in obstaculo:
                x, y = punto
                vertices_obstaculo.append((x, y, self.offset_obstaculos))
                lista_vertices.append(vertices_obstaculo)

        # Uniendo los vértices de cada obstáculo del entorno
        contornos_obstaculos = []
        for vertices in lista_vertices:
            contorno_obstaculo = Line(vertices, closed=True)
            contornos_obstaculos.append(contorno_obstaculo)

        # Triangulando los obstáculos
        poligonos = []
        for contorno in contornos_obstaculos:
            poligono = contorno.clone().triangulate().cap(True)
            poligonos.append(poligono)

        # Extruyendo los poligonos triangulados
        poligonos_extruidos = []
        for poligono in poligonos:
            poligono_extruido = poligono.extrude(self.altura).color([0, 128, 192])
            poligonos_extruidos.append(poligono_extruido)

        # Transformando las coordenas 2D del Start y la Meta a coordenadas 3D
        coordenada_start = (self.start[0], self.start[1], self.offset_trayectoria)
        coordenada_meta = (self.meta[0], self.meta[1], self.offset_trayectoria)

        # Reconstruyendo los puntos de Start y Meta
        punto_start = Point(coordenada_start, c="green", r=14)
        # punto_meta = Star3D(pos=coordenada_meta, c="red", r=7, alpha=1)
        punto_meta = Point(coordenada_meta, c="red", r=14)

        # Tranformando las coordenadas 2D de los puntos trayectoria a coordenadas 3D
        puntos_transformados = []
        if self.trayectoria is not None:
            for punto in self.trayectoria:
                x = round(punto[0], 2)
                y = round(punto[1], 2)
                puntos_transformados.append((x, y, self.offset_trayectoria))

        # Reconstruyendo los puntos de la trayectoria
        puntos_trayectoria = Points(puntos_transformados[1:-1], c="orange", r=8)

        # Reconstruyendo la trayectoria en función de los puntos transformados
        trayectoria = Line(puntos_transformados, c=[0, 0, 0], lw=3)

        # Dibujando el entorno, los puntos de Start y Meta, y la trayectoria
        self.dibujar(poligonos_extruidos, punto_start, punto_meta, puntos_trayectoria, trayectoria)

    def dibujar(self, poligonos_extruidos, punto_start, punto_meta, puntos_trayectoria, trayectoria):
        # Definiendo los límites del entorno
        limite_x, limite_y = self.limites_entorno
        limite_z = (0, self.altura + self.offset_obstaculos)

        # Etiquetando los labels de los ejes coordenados
        x_labels = []
        y_labels = []
        z_labels = []

        ancho_particion_x = limite_x[1] / 5
        ancho_particion_y = limite_y[1] / 5
        ancho_particion_z = limite_z[1] / 5
        medida_x = 0
        medida_y = 0
        medida_z = 0
        for x in range(5):
            x_labels.append((x * ancho_particion_x, str(medida_x / 100)))
            medida_x += ancho_particion_x
        for y in range(1, 5):
            medida_y += ancho_particion_y
            y_labels.append((y * ancho_particion_y, str(medida_y / 100)))
        for z in range(1, 5):
            medida_z += ancho_particion_z
            z_labels.append((z * ancho_particion_z, str(medida_z / 100)))

        # Especificando los parámetros para la graficación
        espacio = buildAxes(xrange=limite_x, yrange=limite_y, zrange=limite_z,
                            xLabelSize=0.03, yLabelSize=0.03, zLabelSize=0.03,
                            xTitleSize=0.04, yTitleSize=0.04, zTitleSize=0.04,
                            xtitle="X", ytitle="Y", ztitle="Z", tipSize=0.02,
                            xValuesAndLabels=x_labels, yValuesAndLabels=y_labels,
                            zValuesAndLabels=z_labels, zxGrid2=True)

        # Presentación del dibujo
        show(espacio, poligonos_extruidos, punto_start, punto_meta, trayectoria, viewup="z")
        # Presionar la barra espaciadora para guardar la imagen
        # screenshot("solucion.png")
