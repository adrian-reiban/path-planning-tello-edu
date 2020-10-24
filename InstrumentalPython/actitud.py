from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QPointF
import math


class Actitud(QGraphicsView):
    def __init__(self, parent=None):
        super(Actitud, self).__init__(parent)

        # Configurando el QGraphicsView
        self.setStyleSheet("background: transparent; border: none")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setInteractive(False)
        self.setEnabled(False)

        # Creando la escena
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)

        """Componentes del medidor de actitud"""
        self.back = None
        self.face = None
        self.ring = None
        self.case = None

        """Parámetros de visualización"""
        # Profundidad de los componentes en el Widget
        self.back_z = -30
        self.face_z = -20
        self.ring_z = -10
        self.case_z = 10

        # Tamaño original del medidor de actitud
        self.actitud_altura = 240
        self.actitud_anchura = 240
        self.actitud_centro = QPointF(120.0, 120.0)
        self.actitud_pixel_grado = 1.7

        # Declaración de los parámetros de escala
        self.escala_x = 0.0
        self.escala_y = 0.0

        """Parámetros de control"""
        self.roll = 0.0
        self.pitch = 0.0

        self.face_deltax_actual = 0.0
        self.face_deltax_anterior = 0.0
        self.face_deltay_actual = 0.0
        self.face_deltay_anterior = 0.0

        self.iniciar()

    def iniciar(self):
        # Estableciendo la escala
        self.escala_x = self.width() / self.actitud_anchura
        self.escala_y = self.height() / self.actitud_altura

        # Reseteando los componentes
        self.reset()

        # Estableciendo y configurando los componentes del medidor de actitud
        self.back = QGraphicsSvgItem("../InstrumentalSVG/actitud/adi_back.svg")
        self.back.setCacheMode(QGraphicsItem.NoCache)
        self.back.setZValue(self.back_z)
        self.back.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.back.setTransformOriginPoint(self.actitud_centro)

        self.face = QGraphicsSvgItem("../InstrumentalSVG/actitud/adi_face.svg")
        self.face.setCacheMode(QGraphicsItem.NoCache)
        self.face.setZValue(self.face_z)
        self.face.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face.setTransformOriginPoint(self.actitud_centro)

        self.ring = QGraphicsSvgItem("../InstrumentalSVG/actitud/adi_ring.svg")
        self.ring.setCacheMode(QGraphicsItem.NoCache)
        self.ring.setZValue(self.ring_z)
        self.ring.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.ring.setTransformOriginPoint(self.actitud_centro)

        self.case = QGraphicsSvgItem("../InstrumentalSVG/actitud/adi_case.svg")
        self.case.setCacheMode(QGraphicsItem.NoCache)
        self.case.setZValue(self.case_z)
        self.case.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.case.setTransformOriginPoint(self.actitud_centro)

        self.escena.addItem(self.back)
        self.escena.addItem(self.face)
        self.escena.addItem(self.ring)
        self.escena.addItem(self.case)

        self.centerOn(self.width() / 2.0, self.height() / 2.0)

        # Actualizando el medidor de actitud
        self.actualizar()

    def reset(self):
        self.back = None
        self.face = None
        self.ring = None
        self.case = None

        self.roll = 0.0
        self.pitch = 0.0

        self.face_deltax_actual = 0.0
        self.face_deltax_anterior = 0.0
        self.face_deltay_actual = 0.0
        self.face_deltay_anterior = 0.0

    def reiniciar(self):
        if self.escena:
            self.escena.clear()
            self.iniciar()

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.reiniciar()

    def establecer_roll(self, roll):
        self.roll = roll
        if self.roll < -180.0:
            self.roll = -180.0
        elif self.roll > 180.0:
            self.roll = 180.0

    def establecer_pitch(self, pitch):
        self.pitch = pitch
        if self.pitch < -25.0:
            self.pitch = -25.0
        elif self.pitch > 25.0:
            self.pitch = 25.0

    def actualizar(self):
        # Estableciendo la escala
        self.escala_x = self.width() / self.actitud_anchura
        self.escala_y = self.height() / self.actitud_altura

        self.back.setRotation(- self.roll)
        self.face.setRotation(- self.roll)
        self.ring.setRotation(- self.roll)

        roll_radian = (math.pi * self.roll) / 180.0
        delta = self.actitud_pixel_grado * self.pitch
        self.face_deltax_actual = self.escala_x * delta * math.sin(roll_radian)
        self.face_deltay_actual = self.escala_y * delta * math.cos(roll_radian)

        self.face.moveBy(self.face_deltax_actual - self.face_deltax_anterior,
                         self.face_deltay_actual - self.face_deltay_anterior)

        self.face_deltax_anterior = self.face_deltax_actual
        self.face_deltay_anterior = self.face_deltay_actual

        self.escena.update()
