from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QPointF


class Direccion(QGraphicsView):
    def __init__(self, parent=None):
        super(Direccion, self).__init__(parent)

        # Configurando el QGraphicsView
        self.setStyleSheet("background: transparent; border: none")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setEnabled(False)

        # Creando la escena
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)

        """Componentes del indicador de dirección"""
        self.face = None
        self.case = None

        """Parámetros de visualización"""
        # Profundidad de los componentes en el Widget
        self.face_z = -20
        self.case_z = 10

        # Tamaño original del indicador de dirección
        self.direccion_altura = 240
        self.direccion_anchura = 240
        self.direccion_centro = QPointF(120.0, 120.0)

        # Declaración de los parámetros de escala
        self.escala_x = 0.0
        self.escala_y = 0.0

        """Parámetros de control"""
        self.yaw = 0.0

        self.iniciar()

    def iniciar(self):
        # Estableciendo la escala
        self.escala_x = self.width() / self.direccion_anchura
        self.escala_y = self.height() / self.direccion_altura

        # Reseteando los componentes
        self.reset()

        # Estableciendo y configurando los componentes del indicador de dirección
        self.face = QGraphicsSvgItem("../InstrumentalSVG/direccion/hsi_face.svg")
        self.face.setCacheMode(QGraphicsItem.NoCache)
        self.face.setZValue(self.face_z)
        self.face.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face.setTransformOriginPoint(self.direccion_centro)

        self.case = QGraphicsSvgItem("../InstrumentalSVG/direccion/hsi_case.svg")
        self.case.setCacheMode(QGraphicsItem.NoCache)
        self.case.setZValue(self.case_z)
        self.case.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.case.setTransformOriginPoint(self.direccion_centro)

        self.escena.addItem(self.face)
        self.escena.addItem(self.case)

        self.centerOn(self.width() / 2.0, self.height() / 2.0)

        # Actualizando el indicador de dirección
        self.actualizar()

    def reset(self):
        self.face = None
        self.case = None

        self.yaw = 0.0

    def reiniciar(self):
        if self.escena:
            self.escena.clear()
            self.iniciar()

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.reiniciar()

    def establecer_yaw(self, yaw):
        self.yaw = yaw

    def actualizar(self):
        self.face.setRotation(- self.yaw)
        self.escena.update()
