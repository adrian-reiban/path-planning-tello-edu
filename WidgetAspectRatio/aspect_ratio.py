from PyQt5.QtWidgets import QBoxLayout, QSpacerItem, QWidget


class AspectRatio(QWidget):
    def __init__(self, widget, parent):
        super().__init__(parent)
        self.aspect_ratio = widget.size().width() / widget.size().height()
        self.setLayout(QBoxLayout(QBoxLayout.LeftToRight, self))

        self.layout().addItem(QSpacerItem(0, 0))
        self.layout().addWidget(widget)
        self.layout().addItem(QSpacerItem(0, 0))

    def resizeEvent(self, e):
        ancho = e.size().width()
        alto = e.size().height()

        # Realiza la acción si el widget es demasiado ancho
        if ancho / alto > self.aspect_ratio:
            self.layout().setDirection(QBoxLayout.LeftToRight)
            widget_stretch = alto * self.aspect_ratio
            outer_stretch = (ancho - widget_stretch) / 2 + 0.5

        # Realiza la acción si el widget es demasiado alto
        else:
            self.layout().setDirection(QBoxLayout.TopToBottom)
            widget_stretch = ancho / self.aspect_ratio
            outer_stretch = (alto - widget_stretch) / 2 + 0.5

        self.layout().setStretch(0, outer_stretch)
        self.layout().setStretch(1, widget_stretch)
        self.layout().setStretch(2, outer_stretch)
