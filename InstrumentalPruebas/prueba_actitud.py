import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from WidgetAspectRatio.aspect_ratio import AspectRatio
from InstrumentalPython.actitud import Actitud


class PruebaActitud(QWidget):
    def __init__(self, *args, **kwargs):
        super(PruebaActitud, self).__init__(*args, **kwargs)
        self.setWindowTitle("Medidor de actitud")

        layout = QHBoxLayout()
        self.actitud = Actitud()
        self.actitud.resize(300, 300)
        self.widget_actitud = AspectRatio(self.actitud, self)
        layout.addWidget(self.widget_actitud)
        self.setLayout(layout)
        self.resize(self.actitud.size())

        # Parámetros de control
        self.roll = 0.0
        self.pitch = 0.0

        self.incremento_roll = 1.0
        self.incremento_pitch = 1.0

        # Configuración del temporizador y llamada a la función actualizar
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start()

    def actualizar(self):
        self.roll += self.incremento_roll
        self.pitch += self.incremento_pitch

        if self.roll > 180.0:
            self.incremento_roll = -1.0
        elif self.roll < -180.0:
            self.incremento_roll = 1.0

        if self.pitch > 25.0:
            self.incremento_pitch = -1.0
        elif self.pitch < -25.0:
            self.incremento_pitch = 1.0

        self.actitud.establecer_roll(self.roll)
        self.actitud.establecer_pitch(self.pitch)
        self.actitud.actualizar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PruebaActitud()
    window.show()
    sys.exit(app.exec_())
