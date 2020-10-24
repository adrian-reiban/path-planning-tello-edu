import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from WidgetAspectRatio.aspect_ratio import AspectRatio
from InstrumentalPython.viraje import Viraje


class PruebaViraje(QWidget):
    def __init__(self, *args, **kwargs):
        super(PruebaViraje, self).__init__(*args, **kwargs)
        self.setWindowTitle("Indicador de viraje")

        layout = QHBoxLayout()
        self.viraje = Viraje()
        self.viraje.resize(300, 300)
        self.widget_viraje = AspectRatio(self.viraje, self)
        layout.addWidget(self.widget_viraje)
        self.resize(self.viraje.size())
        self.setLayout(layout)

        # Parámetros de control
        self.tasa_giro = 0.0
        self.deslizamiento = 0.0
        self.incremento_giro = 1.0
        self.incremento_deslizamiento = 1.0

        # Configuración del temporizador y llamada a la función actualizar
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def actualizar(self):
        self.tasa_giro += self.incremento_giro
        self.deslizamiento += self.incremento_deslizamiento

        if self.tasa_giro > 6.0:
            self.incremento_giro = -1.0
        elif self.tasa_giro < -6.0:
            self.incremento_giro = 1.0

        if self.deslizamiento > 15.0:
            self.incremento_deslizamiento = -1.0
        elif self.deslizamiento < -15.0:
            self.incremento_deslizamiento = 1.0

        self.viraje.establecer_tasa_giro(self.tasa_giro)
        self.viraje.establecer_deslizamiento(self.deslizamiento)
        self.viraje.actualizar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PruebaViraje()
    window.show()
    sys.exit(app.exec_())
