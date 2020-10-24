import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from FuncionesGuardado.guardar_odometria import guardar_odometria


class Visualizador(QMainWindow):
    def __init__(self, nombre_entorno, nombre_drones, rutas_referenciales, supervisores):
        super().__init__()
        # Configuración de los parámetros recibidos
        self.nombre_entorno = nombre_entorno
        self.nombre_drones = nombre_drones
        self.rutas_referenciales = rutas_referenciales
        self.supervisores = supervisores

        # Nombre de la ventana
        self.setWindowTitle("Visualizador de Estados del %s" % self.nombre_entorno)

        # Widget principal
        self.widget = QWidget()
        # Layout Principal
        self.layout_principal = QHBoxLayout()
        # Grid layout1: Contiene el graficador de trayectorias y el botón de guardado
        self.grid_layout1 = QGridLayout()
        # Grid layout2: Contiene los graficadores de alturas
        self.grid_layout2 = QGridLayout()

        # Boton Guardar
        self.boton_guardar = QPushButton("Guardar resultados")
        self.boton_guardar.setIcon(QIcon("../Iconos/icons/disk.png"))
        self.boton_guardar.clicked.connect(self.guardar_datos)

        # Widget 3D para la visualización de las trayectorias de los drones
        self.widget_3d = gl.GLViewWidget()
        # Configuración de las grillas para el Widget 3D
        grilla1 = gl.GLGridItem()
        grilla2 = gl.GLGridItem()
        grilla3 = gl.GLGridItem()
        grilla1.rotate(90, 1, 0, 0)     # Plano XZ
        grilla2.rotate(90, 0, 1, 0)     # Plano YZ
        grilla3.rotate(0, 0, 0, 1)      # Plano XY
        grilla1.setSize(7, 7, 0)
        grilla2.setSize(7, 7, 0)
        grilla3.setSize(7, 7, 0)
        grilla1.translate(3.0, -0.5, 3.5)
        grilla2.translate(-0.5, 3.0, 3.5)
        grilla3.translate(3.0, 3.0, 0)
        # Agregando las grillas al Widget 3D
        self.widget_3d.addItem(grilla1)
        self.widget_3d.addItem(grilla2)
        self.widget_3d.addItem(grilla3)
        # Agregando ejes coordenados al Widget 3D
        ejes3d = gl.GLAxisItem(antialias=True)
        ejes3d.setSize(6.5, 6.5, 7)
        self.widget_3d.addItem(ejes3d)

        # Listas para el almacenamiento de datos
        self.trayectorias = []          # Almacenará las trayectorias ejecutadas por los drones
        self.alturas = []               # Almacenará las alturas de los drones
        self.actualizadores3d = []      # Almacenará las referencias para la actualización del grafico 3d
        self.escala_tiempo = []         # Almacenará los valores del tiempo transcurrido
        self.tiempo_transcurrido = 0    # Variable para el conteo total del tiempo

        # Colores de las trayectorias que se dibujarán durante la ejecución del programa
        self.colores_trayectorias = [(0, 128/255, 255/255, 1), (255/255, 128/255, 64/255, 1),
                                     (128/255, 0, 64/255, 1), (128/255, 255/255, 128/255, 1)]

        # Configuración de los graficadores
        self.graficadores2d = []
        self.ubicaciones_graficadores2d = None
        self.ubicaciones_instrumental = None
        self.ubicacion_boton_guardado = None
        numero_drones = len(nombre_drones)
        if numero_drones == 1:
            self.ubicaciones_graficadores2d = [(0, 0, 1, 1)]
        elif numero_drones == 2:
            self.ubicaciones_graficadores2d = [(0, 0, 1, 1), (1, 0, 1, 1)]
        elif numero_drones == 3:
            self.ubicaciones_graficadores2d = [(0, 0, 1, 1), (1, 0, 1, 1), (2, 0, 1, 1)]
        elif numero_drones == 4:
            self.ubicaciones_graficadores2d = [(0, 0, 1, 1), (0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 1, 1)]

        # Agregando el Widget 3D y el botón de guardado al grid layout 1
        self.widget_3d.setMinimumSize(550, 400)     # Tamaño mínimo del Widget 3D
        self.grid_layout1.addWidget(self.widget_3d, 0, 0, 1, 3)
        self.grid_layout1.addWidget(self.boton_guardar, 1, 1, 1, 1)
        # Configurando y agregando los graficadores a los grid layouts respectivos
        for indice, drone in enumerate(nombre_drones):
            self.configuracion_graficador3d(indice)
            self.configuracion_graficadores2d(indice, drone)

        # Configurando la ventana principal
        self.layout_principal.addLayout(self.grid_layout1)
        self.layout_principal.addLayout(self.grid_layout2)
        self.widget.setLayout(self.layout_principal)
        self.setCentralWidget(self.widget)

        # Temporizador para la actualización de los gráficos cada cierto intervalo de tiempo
        self.tiempo_actualizacion = 100  # Tiempo en milisegundos
        self.timer = QTimer(self)
        self.timer.setInterval(self.tiempo_actualizacion)
        self.timer.timeout.connect(self.actualizar_odometria)
        self.timer.start()

    # Configuración inicial para la visualización de las trayectorias
    def configuracion_graficador3d(self, indice):
        ruta_referencial = np.array(self.rutas_referenciales[indice])
        ruta = gl.GLLinePlotItem(pos=ruta_referencial, color="w", width=1, antialias=True)
        trayectoria = gl.GLLinePlotItem(pos=None, color=self.colores_trayectorias[indice], width=3, antialias=True)
        self.widget_3d.addItem(ruta)
        self.widget_3d.addItem(trayectoria)
        # Guardando las referencias para la actualización del gráfico 3d
        self.actualizadores3d.append(trayectoria)
        # Agregando el punto de origen para la graficación de la trayectoria del drone
        self.trayectorias.append([(self.rutas_referenciales[indice][0])])

    # Configurando el aspecto gráfico y los parámetros para la visualización de altura de los drones
    def configuracion_graficadores2d(self, indice, drone):
        widget_trazador = pg.PlotWidget(title="Altura %s" % drone)
        widget_trazador.showGrid(x=True, y=True)
        widget_trazador.setLabel("left", units="cm")
        widget_trazador.setLabel("bottom", units="ms")
        trazador = widget_trazador.plot(pen="r")
        # Agregando el widget graficador al GridLayout en la posición respectiva
        self.grid_layout2.addWidget(widget_trazador, self.ubicaciones_graficadores2d[indice][0],
                                    self.ubicaciones_graficadores2d[indice][1],
                                    self.ubicaciones_graficadores2d[indice][2],
                                    self.ubicaciones_graficadores2d[indice][3])
        # Guardando la referencia a los graficadores
        self.graficadores2d.append(trazador)
        # Estructurando las listas para el almacenamiento de las alturas de los drones y de la escala de tiempo
        self.alturas.append([])
        self.escala_tiempo.append([])

    def actualizar_odometria(self):
        for indice, supervisor in enumerate(self.supervisores):
            vx, vy, vz = supervisor.velocidad()
            # Actualizando el graficador de trayectorias
            if vx is not None and vy is not None and vz is not None:
                # Se invierte el signo en Y & Z debido a que los ejes del drone están invertidos con respecto
                # al sistema coordenado de la mano derecha
                # La distribución de los ejes depende de la manera en que se calibre el drone y de la versión del SDK
                dx_actual = (-vx * self.tiempo_actualizacion / 8000)    # Diferencial de desplazamiento en X
                dy_actual = (vy * self.tiempo_actualizacion / 8000)     # Diferencial de desplazamiento en Y
                dz_actual = (vz * self.tiempo_actualizacion / 7000)     # Diferencial de desplazamiento en Z
                dx_ant, dy_ant, dz_ant = self.trayectorias[indice][-1]
                # Graficando la trayectoria
                self.trayectorias[indice].append((dx_actual + dx_ant, dy_actual + dy_ant, dz_actual + dz_ant))
                self.actualizadores3d[indice].setData(pos=np.array(self.trayectorias[indice]))

            # Actualizando el graficador de altura
            tof, h = supervisor.altura()
            if tof is not None:
                self.alturas[indice].append(tof)
                self.escala_tiempo[indice].append(self.tiempo_transcurrido)
                self.graficadores2d[indice].setData(self.escala_tiempo[indice], self.alturas[indice])

        self.tiempo_transcurrido += self.tiempo_actualizacion

    def guardar_datos(self):
        self.timer.stop()
        self.boton_guardar.setDisabled(True)
        guardar_odometria(self.nombre_entorno, self.rutas_referenciales, self.escala_tiempo,
                          self.trayectorias, self.alturas)
