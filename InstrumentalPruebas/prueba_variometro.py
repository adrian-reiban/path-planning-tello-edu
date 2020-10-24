import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from WidgetAspectRatio.aspect_ratio import AspectRatio
from InstrumentalPython.variometro import Variometro


class PruebaVariometro(QWidget):
    def __init__(self, *args, **kwargs):
        super(PruebaVariometro, self).__init__(*args, **kwargs)
        self.setWindowTitle("Medidor de velocidad vertical")

        layout = QHBoxLayout()
        self.variometro = Variometro()
        self.variometro.resize(300, 300)
        self.widget_variometro = AspectRatio(self.variometro, self)
        layout.addWidget(self.widget_variometro)
        self.resize(self.variometro.size())
        self.setLayout(layout)

        # Parámetros de control
        self.tasa_ascenso = 0.0
        self.incremento = 10.0

        # Configuración del temporizador y llamada a la función actualizar
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def actualizar(self):
        self.tasa_ascenso += self.incremento

        if self.tasa_ascenso > 1000.0:
            self.incremento = -10.0
        if self.tasa_ascenso < -1000.0:
            self.incremento = 10.0
        self.variometro.establecer_tasa_ascenso(self.tasa_ascenso)
        self.variometro.actualizar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PruebaVariometro()
    window.show()
    sys.exit(app.exec_())
