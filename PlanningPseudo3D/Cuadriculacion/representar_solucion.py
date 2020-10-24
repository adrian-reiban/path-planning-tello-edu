"""Solución del entorno"""
from vedo import Grid, Box, Point, Line, buildAxes, show, settings, embedWindow, screenshot
# Mejores fuentes: Bongas, Comae, Kanopus, Quikhand, SmartCouric, Theemim, Normografo
settings.defaultFont = "SmartCouric"
settings.screeshotScale = 2     # Calidad de imagen, el valor debe ser un número entero
embedWindow(False)


class RepresentarSolucion:
    def __init__(self, entorno, start, meta, trayectoria, dimensiones_obstaculo, offset_obstaculos, offset_trayectoria):
        # Entorno 2D
        self.entorno = entorno

        # Número de filas y columnas del entorno
        self.n_filas = None
        self.n_columnas = None

        # Puntos de Start y Meta
        self.start = start
        self.meta = meta

        # Trayectoria
        self.trayectoria = trayectoria

        # Dimensiones de cada obstáculo del entorno
        self.dimensiones_obstaculo = dimensiones_obstaculo

        # Offset en Z de los obstáculos
        self.offset_obstaculos = offset_obstaculos

        # Offset en Z de la trayectoria
        self.offset_trayectoria = offset_trayectoria

        # Confgiuracion inicial
        self.configuracion()

    def configuracion(self):
        # Transformando el entorno 2D a un aspecto 3D
        self.n_filas, self.n_columnas = self.entorno.shape
        entorno_transformado = []
        for fila in range(self.n_filas):
            for columna in range(self.n_columnas):
                if self.entorno[fila, columna] == 1:
                    x = (self.dimensiones_obstaculo[0] * fila) + (self.dimensiones_obstaculo[0] / 2)
                    y = (self.dimensiones_obstaculo[1] * columna) + (self.dimensiones_obstaculo[1] / 2)
                    z = (self.dimensiones_obstaculo[2] / 2) + self.offset_obstaculos
                    cubo = Box(pos=[x, y, z], length=self.dimensiones_obstaculo[0], width=self.dimensiones_obstaculo[1],
                               height=self.dimensiones_obstaculo[2], c="black")
                    # cubo.lineColor(lc="white")
                    entorno_transformado.append(cubo)

        # Transformando las coordenadas 2D del Start y la Meta a coordenadas 3D
        coordenada_start = ((self.start[0] * self.dimensiones_obstaculo[0]) + (self.dimensiones_obstaculo[0] / 2),
                            (self.start[1] * self.dimensiones_obstaculo[1]) + (self.dimensiones_obstaculo[1] / 2),
                            (self.dimensiones_obstaculo[2] / 2) + self.offset_trayectoria)

        coordenada_meta = ((self.meta[0] * self.dimensiones_obstaculo[0]) + (self.dimensiones_obstaculo[0] / 2),
                           (self.meta[1] * self.dimensiones_obstaculo[1]) + (self.dimensiones_obstaculo[1] / 2),
                           (self.dimensiones_obstaculo[2] / 2) + self.offset_trayectoria)

        # Reconstruyendo los puntos de Start y Meta
        punto_start = Point(coordenada_start, c="green", r=15)
        punto_meta = Point(coordenada_meta, c="red", r=15)

        # Tranformando las coordenadas 2D de los puntos trayectoria a coordenadas 3D
        puntos_transformados = []
        if self.trayectoria is not None:
            for coordenada in self.trayectoria:
                x = (coordenada[0] * self.dimensiones_obstaculo[0]) + (self.dimensiones_obstaculo[0] / 2)
                y = (coordenada[1] * self.dimensiones_obstaculo[1]) + (self.dimensiones_obstaculo[1] / 2)
                z = (self.dimensiones_obstaculo[2] / 2) + self.offset_trayectoria
                puntos_transformados.append((x, y, z))

        # Reconstruyendo la trayectoria en función de los puntos transformados
        trayectoria = Line(puntos_transformados, c=[255, 128, 0], lw=3)

        # Dibujando el entorno y los resultados
        self.dibujar(entorno_transformado, punto_start, punto_meta, trayectoria)

    def dibujar(self, entorno_transformado, punto_start, punto_meta, trayectoria, medida_real=False):
        # Definiendo los límites del entorno
        limite_x = (0, (self.n_filas * self.dimensiones_obstaculo[0]) + 0.125 + 0.5)
        limite_y = (0, (self.n_columnas * self.dimensiones_obstaculo[1]) + 0.125 + 0.5)
        limite_z = (0, (self.dimensiones_obstaculo[2] + self.offset_obstaculos) + 0.5)

        x_labels = []
        y_labels = []
        z_labels = []
        # Etiquetando los labels de los ejes coordenados con las medidas reales
        if medida_real:
            medida_x = 0
            medida_y = 0
            medida_z = 0
            for x in range(self.n_filas):
                x_labels.append((x * self.dimensiones_obstaculo[0], str(medida_x)))
                medida_x += self.dimensiones_obstaculo[0]
            for y in range(self.n_columnas):
                y_labels.append((y * self.dimensiones_obstaculo[1], str(medida_y)))
                medida_y += self.dimensiones_obstaculo[1]
            for z in range(1):
                z_labels.append((z * self.dimensiones_obstaculo[2], str(medida_z)))
                medida_z += self.dimensiones_obstaculo[2]
        else:   # Etiquetando los labels de los ejes de acuerdo al número de celda
            for x in range(self.n_filas):
                posicion_x = (x * self.dimensiones_obstaculo[0]) + (self.dimensiones_obstaculo[0] / 2)
                x_labels.append((posicion_x, str(x)))
            for y in range(self.n_columnas):
                posicion_y = (y * self.dimensiones_obstaculo[1]) + (self.dimensiones_obstaculo[1] / 2)
                y_labels.append((posicion_y, str(y)))
            for z in range(1):
                posicion_z = (z * self.dimensiones_obstaculo[2]) + (self.dimensiones_obstaculo[2] / 2)
                z_labels.append((posicion_z, str(z)))

        # Construyendo un plano cuadriculado
        posicion_cuadricula = (self.n_filas * self.dimensiones_obstaculo[0] / 2,
                               self.n_columnas * self.dimensiones_obstaculo[1] / 2, 0)
        plano_cuadriculado = Grid(pos=posicion_cuadricula, sx=self.n_filas * self.dimensiones_obstaculo[0],
                                  sy=self.n_columnas * self.dimensiones_obstaculo[1], sz=0,
                                  resx=self.n_filas, resy=self.n_columnas, c="gray", alpha=1)
        # Especificando los parámetros para la graficación
        espacio = buildAxes(xrange=limite_x, yrange=limite_y, zrange=limite_z,
                            xLabelSize=0.03, yLabelSize=0.03, zLabelSize=0.03,
                            xTitleSize=0.04, yTitleSize=0.04, zTitleSize=0.04,
                            xtitle="X", ytitle="Y", ztitle="Z", tipSize=0.02,
                            xyGrid=False, yzGrid=False,
                            xValuesAndLabels=x_labels, yValuesAndLabels=y_labels,
                            zValuesAndLabels=z_labels)
        # Presentación del dibujo
        show(espacio, plano_cuadriculado, entorno_transformado, punto_start, punto_meta, trayectoria,
             viewup="z")
        # Presionar la barra espaciadora para guardar la imagen
        # screenshot("solucion.png")
