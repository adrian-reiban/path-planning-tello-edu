from panda3d.core import Vec3, CollisionNode, CollisionBox


class Voxel:
    def __init__(self, posicion=(0.0, 0.0, 0.0), escala=(1.0, 1.0, 1.0), textura=None, parent=None):
        self.posicion = Vec3(posicion)
        self.escala = Vec3(escala)

        # Cargando el modelo
        self.voxel = loader.loadModel("../Modelos/EGG/voxel")

        # Estableciendo la posición y la escala
        self.voxel.setPos(self.posicion)
        self.voxel.setScale(self.escala)

        # Agregando textura al voxel
        if textura is not None:
            textura = loader.loadTexture("../Modelos/Texturas/Entorno/" + textura + ".png")
            self.voxel.setTexture(textura)
        else:
            textura = loader.loadTexture("../Modelos/Texturas/Entorno/tile.png")
            self.voxel.setTexture(textura)

        # Agregando colisión al voxel
        nodo_colision = CollisionNode("voxel")
        nodo_colision.addSolid(CollisionBox(Vec3(0.0, 0.0, 0.0), 0.5, 0.5, 0.5))
        self.voxel.attachNewNode(nodo_colision)

        if parent is not None:
            self.voxel.reparentTo(parent)
        else:
            # Dibujando el voxel en la escena
            self.voxel.reparentTo(render)
