import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from WidgetAspectRatio.aspect_ratio import AspectRatio
from InstrumentalPython.altimetro import Altimetro


class PruebaAltimetro(QWidget):
    def __init__(self, *args, **kwargs):
        super(PruebaAltimetro, self).__init__(*args, **kwargs)
        self.setWindowTitle("Medidor de altitud")

        layout = QHBoxLayout()
        self.altimetro = Altimetro()
        self.altimetro.resize(300, 300)
        self.widget_altimetro = AspectRatio(self.altimetro, self)
        layout.addWidget(self.widget_altimetro)
        self.resize(self.altimetro.size())
        self.setLayout(layout)

        # Parámetros de control
        self.altitud = 0.0
        self.incremento = 5.0

        # Configuración del temporizador y llamada a la función actualizar
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def actualizar(self):
        self.altitud += self.incremento

        if self.altitud > 1000:
            self.incremento = -5.0
        if self.altitud < -1000:
            self.incremento = 5.0
        self.altimetro.establecer_altitud(self.altitud)
        self.altimetro.actualizar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PruebaAltimetro()
    window.show()
    sys.exit(app.exec_())
