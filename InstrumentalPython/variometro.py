from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QPointF


class Variometro(QGraphicsView):
    def __init__(self, parent=None):
        super(Variometro, self).__init__(parent)

        # Configurando el QGraphicsView
        self.setStyleSheet("background: transparent; border: none")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setEnabled(False)

        # Creando la escena
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)

        """Componentes del variómetro (VSI)"""
        self.face = None
        self.hand = None
        self.case = None

        """Parámetros de visualización"""
        # Profundidad de los componentes en el Widget
        self.face_z = -20
        self.hand_z = -10
        self.case_z = 10

        # Tamaño original del variómetro
        self.vsi_altura = 240
        self.vsi_anchura = 240
        self.vsi_centro = QPointF(120.0, 120.0)

        # Declaración de los parámetros de escala
        self.escala_x = 0.0
        self.escala_y = 0.0

        """Parámetros de control"""
        self.tasa_ascenso = 0.0

        self.iniciar()

    def iniciar(self):
        # Estableciendo la escala
        self.escala_x = self.width() / self.vsi_anchura
        self.escala_y = self.height() / self.vsi_altura

        # Reseteando los componentes
        self.reset()

        # Estableciendo y configurando los componentes del variómetro
        self.face = QGraphicsSvgItem("../InstrumentalSVG/variometro/vsi_face.svg")
        self.face.setCacheMode(QGraphicsItem.NoCache)
        self.face.setZValue(self.face_z)
        self.face.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face.setTransformOriginPoint(self.vsi_centro)

        self.hand = QGraphicsSvgItem("../InstrumentalSVG/variometro/vsi_hand.svg")
        self.hand.setCacheMode(QGraphicsItem.NoCache)
        self.hand.setZValue(self.hand_z)
        self.hand.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.hand.setTransformOriginPoint(self.vsi_centro)

        self.case = QGraphicsSvgItem("../InstrumentalSVG/variometro/vsi_case.svg")
        self.case.setCacheMode(QGraphicsItem.NoCache)
        self.case.setZValue(self.case_z)
        self.case.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.case.setTransformOriginPoint(self.vsi_centro)

        self.escena.addItem(self.face)
        self.escena.addItem(self.hand)
        self.escena.addItem(self.case)

        self.centerOn(self.width() / 2.0, self.height() / 2.0)

        # Actualizando el variómetro
        self.actualizar()

    def reset(self):
        self.face = None
        self.hand = None
        self.case = None

        self.tasa_ascenso = 0.0

    def reiniciar(self):
        if self.escena:
            self.escena.clear()
            self.iniciar()

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.reiniciar()

    def establecer_tasa_ascenso(self, tasa_ascenso):
        self.tasa_ascenso = tasa_ascenso
        if self.tasa_ascenso < -2000.0:
            self.tasa_ascenso = -2000.0
        elif tasa_ascenso > 2000.0:
            self.tasa_ascenso = 2000.0

    def actualizar(self):
        self.hand.setRotation(self.tasa_ascenso * 0.086)
        self.escena.update()
