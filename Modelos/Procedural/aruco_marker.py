from panda3d.core import Vec3, TransparencyAttrib


class ArucoMarker:
    def __init__(self, identificador=0, posicion=(0.0, 0.0, 0.0), orientacion=(0.0, 0.0, 0.0),
                 escala=(1.0, 1.0, 1.0), parent=None):
        self.identificador = identificador
        self.posicion = Vec3(posicion)
        self.orientacion = Vec3(orientacion)
        self.escala = Vec3(escala)

        # Cargando el modelo
        self.aruco_marker = loader.loadModel("../Modelos/EGG/plano")

        # Estableciendo la posición, la orientación y la escala
        self.aruco_marker.setPos(self.posicion)
        self.aruco_marker.setHpr(self.orientacion)
        self.aruco_marker.setScale(self.escala)

        # Agregando textura al Aruco Marker
        descripcion = "aruco"+str(self.identificador)+".png"
        textura = loader.loadTexture("../Modelos/Texturas/Marker/" + descripcion)
        self.aruco_marker.setTransparency(TransparencyAttrib.M_alpha)
        self.aruco_marker.setTexture(textura)

        if parent is not None:
            self.aruco_marker.reparentTo(parent)
        else:
            # Dibujando el Aruco Marker en la escena
            self.aruco_marker.reparentTo(render)
