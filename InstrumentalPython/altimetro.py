from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QPointF
import math


class Altimetro(QGraphicsView):
    def __init__(self, parent=None):
        super(Altimetro, self).__init__(parent)

        # Configurando el QGraphicsView
        self.setStyleSheet("background: transparent; border: none")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setEnabled(False)

        # Creando la escena
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)

        """Componentes del altímetro"""
        self.face1 = None
        self.face2 = None
        self.face3 = None
        self.hand1 = None
        self.hand2 = None
        self.case = None

        """Parámetros de visualización"""
        # Profundidad de los componentes en el Widget
        self.face1_z = -50
        self.face2_z = -40
        self.face3_z = -30
        self.hand1_z = -20
        self.hand2_z = -10
        self.case_z = 10

        # Tamaño original del altímetro
        self.altimetro_altura = 240
        self.altimetro_anchura = 240
        self.altimetro_centro = QPointF(120.0, 120.0)

        # Declaración de los parámetros de escala
        self.escala_x = 0.0
        self.escala_y = 0.0

        """Parámetros de control"""
        self.altitud = 0.0
        self.presion = 28.0

        self.iniciar()

    def iniciar(self):
        # Estableciendo la escala
        self.escala_x = self.width() / self.altimetro_anchura
        self.escala_y = self.height() / self.altimetro_altura

        # Reseteando los componentes
        self.reset()

        # Estableciendo y configurando los componentes del altímetro
        self.face1 = QGraphicsSvgItem("../InstrumentalSVG/altimetro/alt_face_1.svg")
        self.face1.setCacheMode(QGraphicsItem.NoCache)
        self.face1.setZValue(self.face1_z)
        self.face1.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face1.setTransformOriginPoint(self.altimetro_centro)

        self.face2 = QGraphicsSvgItem("../InstrumentalSVG/altimetro/alt_face_2.svg")
        self.face2.setCacheMode(QGraphicsItem.NoCache)
        self.face2.setZValue(self.face2_z)
        self.face2.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face2.setTransformOriginPoint(self.altimetro_centro)

        self.face3 = QGraphicsSvgItem("../InstrumentalSVG/altimetro/alt_face_3.svg")
        self.face3.setCacheMode(QGraphicsItem.NoCache)
        self.face3.setZValue(self.face3_z)
        self.face3.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face3.setTransformOriginPoint(self.altimetro_centro)

        self.hand1 = QGraphicsSvgItem("../InstrumentalSVG/altimetro/alt_hand_1.svg")
        self.hand1.setCacheMode(QGraphicsItem.NoCache)
        self.hand1.setZValue(self.hand1_z)
        self.hand1.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.hand1.setTransformOriginPoint(self.altimetro_centro)

        self.hand2 = QGraphicsSvgItem("../InstrumentalSVG/altimetro/alt_hand_2.svg")
        self.hand2.setCacheMode(QGraphicsItem.NoCache)
        self.hand2.setZValue(self.hand2_z)
        self.hand2.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.hand2.setTransformOriginPoint(self.altimetro_centro)

        self.case = QGraphicsSvgItem("../InstrumentalSVG/altimetro/alt_case.svg")
        self.case.setCacheMode(QGraphicsItem.NoCache)
        self.case.setZValue(self.case_z)
        self.case.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.case.setTransformOriginPoint(self.altimetro_centro)

        self.escena.addItem(self.face1)
        self.escena.addItem(self.face2)
        self.escena.addItem(self.face3)
        self.escena.addItem(self.hand1)
        self.escena.addItem(self.hand2)
        self.escena.addItem(self.case)

        self.centerOn(self.width() / 2.0, self.height() / 2.0)

        # Actualizando el altímetro
        self.actualizar()

    def reset(self):
        self.face1 = None
        self.face2 = None
        self.face3 = None
        self.hand1 = None
        self.hand2 = None
        self.case = None

        self.altitud = 0.0
        self.presion = 28.0

    def reiniciar(self):
        if self.escena:
            self.escena.clear()
            self.iniciar()

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.reiniciar()

    def establecer_altitud(self, altitud):
        self.altitud = altitud

    def establecer_presion(self, presion):
        self.presion = presion
        if self.presion < 28.0:
            self.presion = 28.0
        elif self.presion > 31.5:
            self.presion = 31.5

    def actualizar(self):
        altitud = math.ceil(self.altitud + 0.5)
        angulo_h1 = self.altitud * 0.036
        angulo_h2 = (altitud % 1000) * 0.36
        angulo_f1 = (self.presion - 28.0) * 100.0
        angulo_f3 = self.altitud * 0.0036

        self.hand1.setRotation(angulo_h1)
        self.hand2.setRotation(angulo_h2)
        self.face1.setRotation(- angulo_f1)
        self.face2.setRotation(angulo_f3)
        self.escena.update()
