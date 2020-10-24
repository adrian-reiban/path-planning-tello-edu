import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from WidgetAspectRatio.aspect_ratio import AspectRatio
from InstrumentalPython.direccion import Direccion


class PruebaDireccion(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Medidor de dirección")

        layout = QHBoxLayout()
        self.direccion = Direccion()
        self.direccion.resize(300, 300)
        self.widget_direccion = AspectRatio(self.direccion, self)
        layout.addWidget(self.widget_direccion)
        self.setLayout(layout)
        self.resize(self.direccion.size())

        # Parámetros de control
        self.yaw = 0.0
        self.incremento = 1.0

        # Configuración del temporizador y llamada a la función actualizar
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def actualizar(self):
        self.yaw += self.incremento

        if self.yaw > 90.0:
            self.incremento = -1.0
        if self.yaw < -90.0:
            self.incremento = 1.0
        self.direccion.establecer_yaw(self.yaw)
        self.direccion.actualizar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PruebaDireccion()
    window.show()
    sys.exit(app.exec_())
