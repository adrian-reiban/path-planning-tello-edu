from panda3d.core import Vec3, TransparencyAttrib


class MissionPad:
    def __init__(self, identificador=0, posicion=(0.0, 0.0, 0.0), orientacion=(0.0, 0.0, 0.0),
                 escala=(1.0, 1.0, 1.0), parent=None):
        self.identificador = identificador
        self.posicion = Vec3(posicion)
        self.orientacion = Vec3(orientacion)
        self.escala = Vec3(escala)

        # Cargando el modelo
        self.mission_pad = loader.loadModel("../Modelos/EGG/plano")

        # Estableciendo la posición, la orientación y la escala
        self.mission_pad.setPos(self.posicion)
        self.mission_pad.setHpr(self.orientacion)
        self.mission_pad.setScale(self.escala)

        # Agregando textura al Mission Pad
        descripcion = "pad"+str(self.identificador)+".png"
        textura = loader.loadTexture("../Modelos/Texturas/Pads/" + descripcion)
        self.mission_pad.setTransparency(TransparencyAttrib.M_alpha)
        self.mission_pad.setTexture(textura)

        if parent is not None:
            self.mission_pad.reparentTo(parent)
        else:
            # Dibujando el Mission Pad en la escena
            self.mission_pad.reparentTo(render)
