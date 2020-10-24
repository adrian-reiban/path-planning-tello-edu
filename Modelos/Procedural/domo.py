from panda3d.core import Vec3


class Domo:
    def __init__(self):
        # Cargando el modelo
        self.domo = loader.loadModel("../Modelos/EGG/domo")

        # Estableciendo la posición y la escala
        self.domo.setPos(Vec3(0.0, 0.0, 0.0))
        self.domo.setScale(10000)

        # Agregando textura al domo
        textura = loader.loadTexture("../Modelos/Texturas/Entorno/cielo.jpg")
        self.domo.setTexture(textura)

        # Dibujando el domo en la escena
        self.domo.reparentTo(render)
