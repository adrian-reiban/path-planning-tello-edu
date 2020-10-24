import sys
import numpy as np
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (TextNode, CollisionTraverser, CollisionHandlerPusher, CollisionNode, CollisionSphere,
                          CollisionHandlerQueue, BitMask32, CollisionRay, Vec3, LQuaternionf)

from direct.gui.DirectGui import (OnscreenText, DirectFrame, DirectLabel, OkCancelDialog, OkDialog,
                                  DirectDialog, DirectEntry, DirectButton)

from Modelos.Procedural.domo import Domo
from Planning3D.construir_entorno3d import ConstruirEntorno3D


class InterfazConstruccion(ShowBase):
    def __init__(self, dimensiones_entorno, dimensiones_voxel, nvoxels_iniciales):
        super().__init__()
        # Cargando un cielo de fondo
        self.domo = Domo()

        # Activando el medidor de fotogramas por segundo
        self.setFrameRateMeter(True)

        # Creando un nodo que albergará a los objetos del entorno 3D
        # Se emplea dicho nodo para informar al traverser que la búsqueda de colisiones se debe efectuar solamente
        # con los objetos que formen parte del nodo
        self.nodo_entorno = self.render.attachNewNode("nodo entorno")

        # Configurando e inicializando la clase ConstruirEntorno3D
        self.dimensiones_entorno = dimensiones_entorno
        self.dimensiones_voxel = dimensiones_voxel
        self.nmax_voxels_iniciales = nvoxels_iniciales  # Número inicial de voxels que contendrá la plataforma
        self.construir_entorno3d = ConstruirEntorno3D(self.dimensiones_entorno, self.dimensiones_voxel,
                                                      self.nmax_voxels_iniciales, self.nodo_entorno)

        # Creando un traverser para la búsqueda de colisiones
        self.traverser = CollisionTraverser("traverser")

        # Configurando un colisionador del tipo Pusher para mantener la cámara alejada de los objetos del entorno
        self.pusher = CollisionHandlerPusher()

        # Creando un objeto de colisión para la cámara
        self.colisionador_camara = self.camera.attachNewNode(CollisionNode("colisionador camara"))
        self.colisionador_camara.node().addSolid(CollisionSphere(0, 0, 0, 1.125))
        self.pusher.addCollider(self.colisionador_camara, self.camera, self.drive.node())
        self.traverser.addCollider(self.colisionador_camara, self.pusher)

        # Creando un manejador de colisiones del tipo Queue para tratar los eventos del rayo de colisión
        self.queue = CollisionHandlerQueue()

        # Configurando el mouse para seleccionar objetos en la escena mediante el uso de colisiones
        self.pickerNode = CollisionNode("puntero mouse")
        self.pickerNp = self.camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.traverser.addCollider(self.pickerNp, self.queue)

        # Parámetros que se usarán para identificar, construir y borrar un voxel del entorno
        self.identificador = None
        self.vector_normal = None

        # Manejando los eventos del teclado y el mouse
        # KeyMap para el registro de eventos del teclado
        self.keymap = {
            "avanzar": False,
            "retroceder": False,
            "izquierda": False,
            "derecha": False,
            "rotar_izquierda": False,
            "rotar_derecha": False,
            "subir": False,
            "bajar": False,
            "pitch_up": False,
            "pitch_down": False,
            "item_siguiente": False,
            "item_anterior": False
        }
        # Eventos del teclado
        self.accept("escape", self.cuadros_dialogo, ["salir"])
        self.accept("g", self.cuadros_dialogo, ["guardar"])

        self.accept("w", self.actualizar_keymap, ["avanzar", True])
        self.accept("w-up", self.actualizar_keymap, ["avanzar", False])
        self.accept("s", self.actualizar_keymap, ["retroceder", True])
        self.accept("s-up", self.actualizar_keymap, ["retroceder", False])
        self.accept("a", self.actualizar_keymap, ["izquierda", True])
        self.accept("a-up", self.actualizar_keymap, ["izquierda", False])
        self.accept("d", self.actualizar_keymap, ["derecha", True])
        self.accept("d-up", self.actualizar_keymap, ["derecha", False])
        self.accept("arrow_left", self.actualizar_keymap, ["rotar_izquierda", True])
        self.accept("arrow_left-up", self.actualizar_keymap, ["rotar_izquierda", False])
        self.accept("arrow_right", self.actualizar_keymap, ["rotar_derecha", True])
        self.accept("arrow_right-up", self.actualizar_keymap, ["rotar_derecha", False])
        self.accept("arrow_up", self.actualizar_keymap, ["subir", True])
        self.accept("arrow_up-up", self.actualizar_keymap, ["subir", False])
        self.accept("arrow_down", self.actualizar_keymap, ["bajar", True])
        self.accept("arrow_down-up", self.actualizar_keymap, ["bajar", False])
        self.accept("wheel_up", self.actualizar_keymap, ["pitch_up", True])
        self.accept("wheel_down", self.actualizar_keymap, ["pitch_down", True])
        self.accept("q", self.actualizar_keymap, ["item_anterior", True])
        self.accept("q-up", self.actualizar_keymap, ["item_anterior", False])
        self.accept("e", self.actualizar_keymap, ["item_siguiente", True])
        self.accept("e-up", self.actualizar_keymap, ["item_siguiente", False])

        # Eventos del mouse
        self.accept("mouse1", self.agregar_voxel)
        self.accept("mouse3", self.eliminar_voxel)

        # Deshabilitando el control por defecto de la cámara y posicionando la cámara en el entorno
        self.disableMouse()
        self.posicionar_camara()

        # Loop
        self.taskMgr.add(self.update, "update")

        # Agregando instrucciones sobre el uso del programa
        self.lista_objetos_onscreen = []
        self.agregar_instrucciones()

        # Colocando un panel para la interfaz GUI
        self.frame_principal = None
        self.frame_gui = None
        self.nombre_elementos = []
        self.elementos_gui = []
        self.indice_elemento = 0
        self.panel_gui()
        # Seleccionando por defecto el primer elemento del panel
        self.seleccion_elemento(self.indice_elemento)

        # Declaración de variables para objetos del tipo DirectDialog y DirectEntry
        self.dialogo_guardar = None
        self.dialogo_salir = None
        self.entrada_texto = None
        self.dialogo_advertencia = None

    # Actualizando el KeyMap
    def actualizar_keymap(self, clave, valor):
        self.keymap[clave] = valor

    # Loop
    def update(self, task):
        dt = globalClock.getDt()
        self.eventos_puntero()
        self.mover_camara(dt)
        self.eventos_gui()
        return task.cont

    def posicionar_camara(self):
        angulo_horizontal, _ = self.cam.node().getLens().getFov()
        if self.dimensiones_entorno[0] > self.nmax_voxels_iniciales * self.dimensiones_voxel[0]:
            centro_x = ((self.nmax_voxels_iniciales / 2) * self.dimensiones_voxel[0]) - self.dimensiones_voxel[0] / 2
        else:
            centro_x = (self.dimensiones_entorno[0] / 2) - self.dimensiones_voxel[0] / 2

        if self.dimensiones_entorno[1] > self.nmax_voxels_iniciales * self.dimensiones_voxel[1]:
            centro_y = self.nmax_voxels_iniciales * self.dimensiones_voxel[1] / 2
        else:
            centro_y = self.dimensiones_entorno[1] / 2

        posicion_x = centro_x
        posicion_y = posicion_x / np.tan(angulo_horizontal / 2)
        posicion_z = self.dimensiones_voxel[2] * 8
        pitch = (np.arctan(posicion_z / (posicion_y + centro_y))) * 180 / np.pi
        self.camera.setPosHpr(posicion_x, -posicion_y, posicion_z, 0, -pitch, 0)

    def mover_camara(self, dt):
        angulo = self.camera.getH() * np.pi / 180
        q = LQuaternionf(np.cos(angulo / 2), 0, 0, np.sin(angulo / 2))
        # Cuaterniones de dirección local que refieren al sistema de la cámara
        vcx = LQuaternionf(0, 1, 0, 0)  # Cuaternión puro que representa al eje lateral derecho de la cámara
        vcy = LQuaternionf(0, 0, 1, 0)  # Cuaternión puro que representa al eje frontal de la cámara

        # Vectores de dirección de la cámara referente al sistema coordenado global
        vgx = (q.conjugate() * vcx * q).getAxis()
        vgy = (q.conjugate() * vcy * q).getAxis()

        if self.keymap["avanzar"]:
            self.camera.setPos(self.camera.getPos() + (vgy * 5 * dt))
        if self.keymap["retroceder"]:
            self.camera.setPos(self.camera.getPos() + (vgy * -5 * dt))
        if self.keymap["izquierda"]:
            self.camera.setPos(self.camera.getPos() + (vgx * -5 * dt))
        if self.keymap["derecha"]:
            self.camera.setPos(self.camera.getPos() + (vgx * 5 * dt))
        if self.keymap["rotar_izquierda"]:
            self.camera.setH(self.camera.getH() + 30 * dt)
        if self.keymap["rotar_derecha"]:
            self.camera.setH(self.camera.getH() - 30 * dt)
        if self.keymap["subir"]:
            self.camera.setPos(self.camera.getPos() + Vec3(0, 0, 5 * dt))
        if self.keymap["bajar"]:
            self.camera.setPos(self.camera.getPos() + Vec3(0, 0, -5 * dt))
        if self.keymap["pitch_up"]:
            self.camera.setP(self.camera.getP() + 50 * dt)
            self.keymap["pitch_up"] = False
        if self.keymap["pitch_down"]:
            self.camera.setP(self.camera.getP() - 50 * dt)
            self.keymap["pitch_down"] = False

    def eventos_gui(self):
        # Eventos referentes a la selección de los items
        if self.keymap["item_siguiente"]:
            if self.indice_elemento < len(self.elementos_gui) - 1:
                self.indice_elemento += 1
                self.seleccion_elemento(self.indice_elemento, "avanzar")
            self.keymap["item_siguiente"] = False

        if self.keymap["item_anterior"]:
            if self.indice_elemento >= 1:
                self.indice_elemento -= 1
                self.seleccion_elemento(self.indice_elemento, "reversa")
            self.keymap["item_anterior"] = False

    def eventos_puntero(self):
        if self.identificador is not None:
            self.construir_entorno3d.deseleccionar_voxel(self.identificador)
            self.identificador = None

        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            self.pickerRay.setFromLens(self.camNode, x, y)
            self.traverser.traverse(self.nodo_entorno)

            if self.queue.getNumEntries() > 0:
                self.queue.sortEntries()
                objeto_seleccionado = self.queue.getEntry(0).getIntoNodePath()
                objeto_seleccionado = objeto_seleccionado.findNetTag("voxel")

                if not objeto_seleccionado.isEmpty():
                    self.identificador = int(objeto_seleccionado.getNetTag("voxel"))

                    # Seleccionando el voxel apuntado
                    self.construir_entorno3d.seleccionar_voxel(self.identificador)

                    # Obteniendo el vector normal a la superficie de colisión
                    self.vector_normal = self.queue.getEntry(0).getSurfaceNormal(objeto_seleccionado)
                    self.vector_normal.normalize()

    def agregar_voxel(self):
        if self.identificador is not None:
            seleccion = self.nombre_elementos[self.indice_elemento]
            # Verificación de nombres
            # El valor de la selección, referencia al nombre de la textura que se aplicará al objeto.
            # Las texturas simples no llevan el identificador uv al inicio del nombre.
            # De acuerdo con las condiciones, se identifica el tipo de textura; si se trata de una textura simple
            # el valor del objeto se lo establece en 0; caso contrario se establece el valor de 1, ya que la textura
            # es del tipo UV Map, y por ende, se debe llamar al objeto de la clase correspondiente para aplicar dicha
            # textura.
            valor = seleccion.split("_", 1)
            if len(valor) == 2 and valor[0] == "uv":
                tipo_elemento = (1, seleccion)
            else:
                tipo_elemento = (0, seleccion)

            self.construir_entorno3d.agregar_voxel(tipo_elemento, self.identificador, self.vector_normal)

    def eliminar_voxel(self):
        if self.identificador is not None:
            self.construir_entorno3d.eliminar_voxel(self.identificador)

    # Agrega instrucciones en la pantalla acerca del uso del programa
    def agregar_instrucciones(self):
        instrucciones = ["[ESC]: Salir", "[G]: Guadar", "[Q, E]: Seleccionar item", "[W]: Avanzar",
                         "[S]: Retroceder",
                         "[A]: Izquierda", "[D]: Derecha", "[Flecha izquierda]: Girar derecha",
                         "[Flecha derecha]: Girar izquierda", "[Flecha superior]: Subir",
                         "[Flecha inferior]: Bajar"]
        posicion = 0.06
        for instruccion in instrucciones:
            texto_pantalla = OnscreenText(
                text=instruccion,
                align=TextNode.ALeft,
                scale=0.05,
                style=1,
                fg=(1, 1, 1, 1),
                shadow=(0, 0, 0, 1),
                pos=(0.08, -posicion, -0.04),
                parent=base.a2dTopLeft
            )
            self.lista_objetos_onscreen.append(texto_pantalla)
            posicion += 0.06

    def guardar_entorno(self, objeto):
        texto = objeto.get()
        if texto and not texto.isspace():
            # Eliminando todos los espacios en blanco de la cadena
            texto = texto.replace(" ", "")
            self.entrada_texto.hide()
            self.entrada_texto.destroy()
            self.entrada_texto = None
            respuesta = self.construir_entorno3d.guardar_entorno(texto)
            if not respuesta:
                self.cuadros_dialogo("advertencia")

    def salir_programa(self, args):
        if args == 1:
            self.dialogo_salir.hide()
            self.dialogo_salir.destroy()
            self.dialogo_salir = None
            self.eliminar_objetos_pantalla()
            sys.exit()
        else:
            self.dialogo_salir.hide()
            self.dialogo_salir.destroy()
            self.dialogo_salir = None

    def cuadros_dialogo(self, seleccion):
        condiciones_extra = (self.dialogo_guardar is None) and (self.dialogo_salir is None) and \
                            (self.dialogo_advertencia is None)
        if seleccion == "guardar" and condiciones_extra:
            self.dialogo_guardar = OkCancelDialog(
                text="¿Desea guardar el entorno?",
                buttonTextList=["Aceptar", "Cancelar"],
                fadeScreen=0.6,
                command=self.cuadro_texto,
                parent=self.frame_principal
            )
            self.dialogo_guardar.show()
        elif seleccion == "salir" and condiciones_extra:
            self.dialogo_salir = OkCancelDialog(
                text="¿Desea salir del entorno?",
                buttonTextList=["Aceptar", "Cancelar"],
                fadeScreen=0.6,
                command=self.salir_programa,
                parent=self.frame_principal
            )
            self.dialogo_salir.show()
        elif seleccion == "advertencia" and condiciones_extra:
            self.dialogo_advertencia = OkDialog(
                text="El nombre propuesto ya existe",
                buttonTextList=["Aceptar"],
                fadeScreen=0.6,
                command=self.cuadro_texto,
                parent=self.frame_principal
            )
            self.dialogo_advertencia.show()

    def cuadro_texto(self, args):
        # Eliminando el cuadro de diálogo guardar
        if self.dialogo_guardar is not None:
            self.dialogo_guardar.hide()
            self.dialogo_guardar.destroy()
            self.dialogo_guardar = None

        # Eliminando el cuadro de diálogo de advertencia
        if self.dialogo_advertencia is not None:
            self.dialogo_advertencia.hide()
            self.dialogo_advertencia.destroy()
            self.dialogo_advertencia = None

        # Mostrando el cuadro de entrada de texto
        if args == 1:
            self.entrada_texto = DirectDialog(
                frameSize=(-0.55, 0.55, -0.3, 0.3),
                fadeScreen=0.6,
                parent=self.frame_principal
            )

            DirectLabel(
                text="Escriba el nombre de su archivo",
                scale=0.07,
                pos=(0, 0, 0.15),
                parent=self.entrada_texto
            )

            texto = DirectEntry(
                frameColor=(1, 1, 1, 1),
                scale=0.07,
                width=14,
                numLines=1,
                focus=1,
                suppressKeys=1,
                suppressMouse=1,
                pos=(-0.49, 0, 0),
                parent=self.entrada_texto
            )

            DirectButton(
                text="Aceptar",
                pos=(0, 0, -0.2),
                scale=0.07,
                command=self.guardar_entorno,
                extraArgs=[texto],
                parent=self.entrada_texto
            )

            self.entrada_texto.show()

    def panel_gui(self):
        self.frame_principal = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 1, -1, 1),
            pos=(0, 0, 0),
            parent=base.aspect2d
        )
        self.frame_principal.setTransparency(True)

        self.frame_gui = DirectFrame(
            frameColor=(0.5, 0.5, 0.5, 0.25),
            frameSize=(-0.5, 0.5, -0.38, 0.38),
            pos=(0, 0, -0.50),
            parent=self.frame_principal
        )
        self.frame_gui.setTransparency(True)

        self.nombre_elementos = ["tile", "caja", "barro", "ladrillo",
                                 "piedra", "hierva", "lava", "agua",
                                 "rojo", "amarillo", "purpura", "uv_grass"]
        ruta = "../Modelos/Items/"
        posicion_elemento_y = 0.38
        separacion_horizontal = 0.04
        separacion_vertical = 0.04
        indice_elemento = 0
        for fila in range(3):
            posicion_elemento_x = -0.5
            posicion_elemento_y -= (separacion_vertical + 0.1)
            for columna in range(4):
                posicion_elemento_x += (separacion_horizontal + 0.1)
                label_elemento = DirectLabel(
                    frameColor=(0, 0, 0, 0),
                    frameSize=(-0.1, 0.1, -0.1, 0.1),
                    pos=(posicion_elemento_x, 0, posicion_elemento_y),
                    image=ruta + self.nombre_elementos[indice_elemento] + ".png",
                    image_scale=0.13,
                    parent=self.frame_gui
                )
                indice_elemento += 1
                self.elementos_gui.append(label_elemento)
                posicion_elemento_x += 0.1
            posicion_elemento_y -= 0.1

    def seleccion_elemento(self, indice_elemento, condicion=" "):
        alpha = 0.6
        # Las condiciones de avanzar y reversa, eliminan la "selección" del item anterior al cambiar el valor
        # del alpha de color
        if condicion == "avanzar":
            elemento_anterior = self.elementos_gui[indice_elemento - 1]
            elemento_anterior["frameColor"] = (0, 0, 0, 0)
        elif condicion == "reversa":
            elemento_anterior = self.elementos_gui[indice_elemento + 1]
            elemento_anterior["frameColor"] = (0, 0, 0, 0)

        # Selecciona el item de acuerdo al índice suministrado
        elemento_actual = self.elementos_gui[indice_elemento]
        elemento_actual["frameColor"] = (0, 0, 0, alpha)

    def eliminar_objetos_pantalla(self):
        # Eliminando el cielo de fondo
        self.domo.domo.detachNode()
        self.domo.domo.removeNode()
        self.domo = None

        # Desactivando el contador de FPS
        self.setFrameRateMeter(False)

        # Eliminando las instrucciones del programa
        for instruccion in self.lista_objetos_onscreen:
            instruccion.hide()
            instruccion.destroy()
        self.lista_objetos_onscreen = None

        # Eliminando el panel gui
        self.frame_principal.hide()
        self.frame_principal.destroy()
        self.frame_principal = None

        # Eliminando las entradas manejadas por el Handler Queue
        self.queue.clearEntries()

        # Eliminando los colisionadores manejados por el pusher y el traverser
        self.pusher.clearColliders()
        self.traverser.clearColliders()

        # Eliminando el picker node
        self.pickerNp.removeNode()
        self.pickerNp = None

        # Eliminando todos los objetos vinculados al render
        for nodo in self.render.getChildren():
            nodo.removeNode()

        # Removiendo las tareas e ignorando todos los eventos
        self.taskMgr.remove("update")
        self.ignoreAll()


def calculo_rendimiento(dimensiones_entorno, dimensiones_voxel):
    dimensiones_minimas_entorno = (2, 2, 2)         # Dimensiones mínimas del entorno
    dimensiones_maximas_entorno = (5, 5, 5)         # Dimensiones máximas del entorno
    dimensiones_minimas_voxel = (0.5, 0.5, 0.5)     # Dimensiones mínimas del voxel
    dimensiones_maximas_voxel = (1, 1, 1)           # Dimensiones máximas del voxel
    nmax_voxels = 10    # Número máximo de voxels que podrá contener cada lado del entorno
    respuesta = False   # Respuesta que retornará si las condiciones no se cumplen

    condicion1 = dimensiones_minimas_entorno[0] <= dimensiones_entorno[0] <= dimensiones_maximas_entorno[0]
    condicion2 = dimensiones_minimas_entorno[1] <= dimensiones_entorno[1] <= dimensiones_maximas_entorno[1]
    condicion3 = dimensiones_minimas_entorno[2] <= dimensiones_entorno[2] <= dimensiones_maximas_entorno[2]
    condicion4 = dimensiones_voxel[0] == dimensiones_voxel[1]
    condicion5 = dimensiones_voxel[1] == dimensiones_voxel[2]
    condicion6 = dimensiones_minimas_voxel[0] <= dimensiones_voxel[0] <= dimensiones_maximas_voxel[0]
    condicion7 = dimensiones_minimas_voxel[1] <= dimensiones_voxel[1] <= dimensiones_maximas_voxel[1]
    condicion8 = dimensiones_minimas_voxel[2] <= dimensiones_voxel[2] <= dimensiones_maximas_voxel[2]

    if condicion1 or condicion2 or condicion3:
        if condicion4 and condicion5:
            if condicion6 and condicion7 and condicion8:
                nvoxels_x = int(dimensiones_entorno[0] / dimensiones_voxel[0])
                nvoxels_y = int(dimensiones_entorno[1] / dimensiones_voxel[1])
                nvoxels_z = int(dimensiones_entorno[2] / dimensiones_voxel[2])

                # Futuro trabajo en esta sección
                if (nvoxels_x > nmax_voxels) or (nvoxels_y > nmax_voxels) or (nvoxels_z > nmax_voxels):
                    print("Número excesivo de voxels para el entorno; el número máximo de voxels admitidos para "
                          "el largo, el alto y el ancho es de " + str(nmax_voxels) + ".\n"
                          "Aumente las dimensiones del voxel en un valor máximo de 1 o reduzca las dimensiones "
                                                                                     "de su entorno.")
                else:
                    respuesta = True
            else:
                print("Las dimensiones de los voxels deben ser mayor o igual a %s y menor o igual a %s" %
                      (dimensiones_minimas_voxel, dimensiones_maximas_voxel))
        else:
            print("Las dimensiones de los voxels en el ancho, el largo y la altura deben ser las mismas")
    else:
        print("No se puede construir el entorno propuesto\n"
              "Las dimensiones mínimas que debe tener el entorno son: "
              "2 metros de ancho x 2 metros de largo x 2 metros de alto"
              "\nY las dimensiones máximas:"
              "5 metros de ancho x 5 metros de largo x 5 metros de alto")
    return respuesta
