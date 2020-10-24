from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QPointF


class Viraje(QGraphicsView):
    def __init__(self, parent=None):
        super(Viraje, self).__init__(parent)

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
        self.back = None
        self.ball = None
        self.face1 = None
        self.face2 = None
        self.mark = None
        self.case = None

        """Parámetros de visualización"""
        # Profundidad de los componentes en el Widget
        self.back_z = -70
        self.ball_z = -60
        self.face1_z = -50
        self.face2_z = -40
        self.mark_z = -30
        self.case_z = 10

        # Tamaño original del indicador de dirección
        self.viraje_altura = 240
        self.viraje_anchura = 240
        self.viraje_centro = QPointF(120.0, 120.0)
        self.centro_marca = QPointF(120.0, 120.0)
        self.centro_esfera = QPointF(120.0, -36.0)

        # Declaración de los parámetros de escala
        self.escala_x = 0.0
        self.escala_y = 0.0

        """Parámetros de control"""
        self.tasa_giro = 0.0
        self.deslizamiento = 0.0

        self.iniciar()

    def iniciar(self):
        # Estableciendo la escala
        self.escala_x = self.width() / self.viraje_anchura
        self.escala_y = self.height() / self.viraje_altura

        # Reseteando los componentes
        self.reset()

        # Estableciendo y configurando los componentes del indicador de dirección
        self.back = QGraphicsSvgItem("../InstrumentalSVG/viraje/tc_back.svg")
        self.back.setCacheMode(QGraphicsItem.NoCache)
        self.back.setZValue(self.back_z)
        self.back.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.back.setTransformOriginPoint(self.viraje_centro)

        self.ball = QGraphicsSvgItem("../InstrumentalSVG/viraje/tc_ball.svg")
        self.ball.setCacheMode(QGraphicsItem.NoCache)
        self.ball.setZValue(self.ball_z)
        self.ball.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.ball.setTransformOriginPoint(self.centro_esfera)

        self.face1 = QGraphicsSvgItem("../InstrumentalSVG/viraje/tc_face_1.svg")
        self.face1.setCacheMode(QGraphicsItem.NoCache)
        self.face1.setZValue(self.face1_z)
        self.face1.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face1.setTransformOriginPoint(self.viraje_centro)

        self.face2 = QGraphicsSvgItem("../InstrumentalSVG/viraje/tc_face_2.svg")
        self.face2.setCacheMode(QGraphicsItem.NoCache)
        self.face2.setZValue(self.face2_z)
        self.face2.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.face2.setTransformOriginPoint(self.viraje_centro)

        self.mark = QGraphicsSvgItem("../InstrumentalSVG/viraje/tc_mark.svg")
        self.mark.setCacheMode(QGraphicsItem.NoCache)
        self.mark.setZValue(self.mark_z)
        self.mark.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.mark.setTransformOriginPoint(self.centro_marca)

        self.case = QGraphicsSvgItem("../InstrumentalSVG/viraje/tc_case.svg")
        self.case.setCacheMode(QGraphicsItem.NoCache)
        self.case.setZValue(self.case_z)
        self.case.setTransform(QTransform.fromScale(self.escala_x, self.escala_y), True)
        self.case.setTransformOriginPoint(self.viraje_centro)

        self.escena.addItem(self.back)
        self.escena.addItem(self.ball)
        self.escena.addItem(self.face1)
        self.escena.addItem(self.face2)
        self.escena.addItem(self.mark)
        self.escena.addItem(self.case)

        self.centerOn(self.width() / 2.0, self.height() / 2.0)

        # Actualizando el indicador de dirección
        self.actualizar()

    def reset(self):
        self.case = None

        self.tasa_giro = 0.0
        self.deslizamiento = 0.0

    def reiniciar(self):
        if self.escena:
            self.escena.clear()
            self.iniciar()

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.reiniciar()

    def establecer_tasa_giro(self, tasa_giro):
        self.tasa_giro = tasa_giro
        if self.tasa_giro < -6.0:
            self.tasa_giro = -6.0
        elif self.tasa_giro > 6.0:
            self.tasa_giro = 6.0

    def establecer_deslizamiento(self, deslizamiento):
        self.deslizamiento = deslizamiento
        if self.deslizamiento < -15.0:
            self.deslizamiento = -15.0
        elif self.deslizamiento > 15.0:
            self.deslizamiento = 15.0

    def actualizar(self):
        self.escala_x = self.width() / self.viraje_anchura
        self.escala_y = self.height() / self.viraje_altura

        self.ball.setRotation(- self.deslizamiento)
        angulo = (self.tasa_giro / 3.0) * 20.0
        self.mark.setRotation(angulo)

        self.escena.update()
