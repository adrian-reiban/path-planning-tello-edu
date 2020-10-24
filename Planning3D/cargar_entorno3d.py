import sys
import numpy as np
import copy

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (Vec3, Vec4, LineSegs, TextNode, NodePath, AmbientLight, DirectionalLight, LQuaternionf)
from direct.gui.DirectGui import (OnscreenText, DirectLabel, OkCancelDialog, OkDialog, DirectDialog, DirectEntry,
                                  DirectButton, DirectScrolledFrame, DGG)

from Modelos.Procedural.domo import Domo
from Modelos.Procedural.voxel import Voxel
from Modelos.Procedural.voxel_map import VoxelMap
from Modelos.Procedural.mission_pad import MissionPad
from Modelos.Procedural.aruco_marker import ArucoMarker
from FuncionesGuardado.matrices import (crear_directorio, leer_matriz, guardar_matriz)
from FuncionesGuardado.texto import construir_fichero

from Algoritmos.Algoritmos3D.a_star_swarm import AStar3DSwarm


class CargarEntorno(ShowBase):
    def __init__(self, nombre_directorio):
        super().__init__()
        # Cargando un cielo de fondo
        self.domo = Domo()

        # Agregando iluminación al entorno
        self.iluminar_entorno()

        # Activando el medidor de fotogramas por segundo
        self.setFrameRateMeter(True)

        # Guardando el nombre del directorio
        self.nombre_directorio = nombre_directorio

        # Parámetros del entorno
        self.entorno, self.objetos, self.dimensiones_voxel, self.dimensiones_entorno = abrir_entorno(nombre_directorio)

        # Coordenadas del Start y la Meta
        self.coordenadas_start = None
        self.coordenadas_meta = None

        # Especificando la variable que referenciará un objeto del algoritmo A*
        # Posteriormente se ingresarán las coordenadas del Start y Meta para su ejecución
        self.algoritmo = None

        # Trayectorias3D obtenidas por el algoritmo A*
        self.trayectorias_referenciales = None  # Usadas para la representación en pantalla
        self.trayectorias_reales = None         # Para ser ejecutadas por los drones en el entorno real

        # Creando nodos para clasificar los elementos que se agregarán al entorno
        self.nodo_entorno = self.render.attachNewNode("nodo entorno")
        self.nodo_start_meta = self.render.attachNewNode("nodo start-meta")
        self.nodo_trayectorias_dibujadas = self.render.attachNewNode("nodo trayectorias dibujadas")

        # Construyendo el entorno
        self.construir_entorno()

        # Deshabilitando el control por defecto de la cámara y posicionando la cámara en el entorno
        self.disableMouse()
        self.posicionar_camara()

        # Agregando el menú de instrucciones
        self.lista_objetos_onscreen = []
        self.agregar_instrucciones()

        # Manejando los eventos del teclado
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
            "pitch_down": False
        }
        # Eventos del teclado
        self.accept("escape", self.control_menu, ["salir"])
        self.accept("t", self.control_menu, ["insertar_start_meta"])
        self.accept("y", self.control_menu, ["calcular_trayectorias"])
        self.accept("i", self.control_menu, ["guardar_trayectorias"])

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

        # Variables de referencia a los cuadros de diálogo
        self.dialogo_salir = None
        self.dialogo_numero_drones = None
        self.dialogo_ingresar_coordenadas = None
        self.dialogo_advertencia_coordenadas = None
        self.dialogo_ejecutar_algoritmo = None
        self.dialogo_advertencia_algoritmo = None
        self.dialogo_guardar_trayectorias = None
        self.dialogo_respuesta_guardar_trayectorias = None
        self.dialogo_advertencia_comando = None

        # Máximo número de drones soportados
        self.numero_drones = 4

        # Banderas que impiden la ejecución de una acción del menú de opciones
        self.ejecucion_algoritmo = False
        self.proceso_guardado = False

        # Loop
        self.taskMgr.add(self.update, "update")

    # Loop
    def update(self, task):
        dt = globalClock.getDt()
        self.mover_camara(dt)
        return task.cont

    # Actualizando el KeyMap
    def actualizar_keymap(self, clave, valor):
        self.keymap[clave] = valor

    def iluminar_entorno(self):
        # Agregando luz a la escena
        # Luz ambiental
        luz_ambiental = AmbientLight("luz ambiente")
        luz_ambiental.setColor(Vec4(0.2, 0.1, 0.1, 1.0))
        luz_ambiental.setColorTemperature(6500)
        node_path_ambiental = self.render.attachNewNode(luz_ambiental)
        self.render.setLight(node_path_ambiental)
        # Luz direccional
        luz_direccional = DirectionalLight("luz direccional")
        luz_direccional.setColor(Vec4(0.2, 0.1, 0.1, 1.0))
        node_path_direccional = self.render.attachNewNode(luz_direccional)
        node_path_direccional.setHpr(45, -45, 0)
        self.render.setLight(node_path_direccional)
        # Activando sombras
        self.render.setShaderAuto()

    def posicionar_camara(self):
        angulo_horizontal, _ = self.cam.node().getLens().getFov()

        centro_x = (self.dimensiones_entorno[0] / 2) - (self.dimensiones_voxel[0] / 2)
        centro_y = (self.dimensiones_entorno[1] / 2) - (self.dimensiones_voxel[1] / 2)
        centro_z = (self.dimensiones_entorno[2] / 2) - (self.dimensiones_voxel[2] / 2)

        posicion_x = centro_x
        posicion_y = (self.dimensiones_entorno[0] / 2) / np.tan(angulo_horizontal * np.pi / 360)
        posicion_y += self.dimensiones_voxel[1] / 2
        posicion_z = centro_z
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

    # Agrega instrucciones en la pantalla acerca del uso del programa
    def agregar_instrucciones(self):
        instrucciones = ["[ESC]: Salir", "[T]: Insertar Start y Meta", "[Y]: Calcular trayectorias",
                         "[I]: Guardar trayectorias",
                         "[W]: Avanzar", "[S]: Retroceder", "[A]: Izquierda", "[D]: Derecha",
                         "[Flecha izquierda]: Girar derecha", "[Flecha derecha]: Girar izquierda",
                         "[Flecha superior]: Subir", "[Flecha inferior]: Bajar"]
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

    def control_menu(self, seleccion):
        condiciones_extra = (self.dialogo_salir is None) and (self.dialogo_numero_drones is None) and \
                            (self.dialogo_ingresar_coordenadas is None) and \
                            (self.dialogo_advertencia_coordenadas is None) and \
                            (self.dialogo_ejecutar_algoritmo is None) and (self.ejecucion_algoritmo is False) and \
                            (self.proceso_guardado is False) and (self.dialogo_guardar_trayectorias is None)

        if seleccion == "salir" and condiciones_extra:
            self.dialogo_salir = OkCancelDialog(
                text="¿Está seguro que desea salir del entorno?",
                buttonTextList=["Aceptar", "Cancelar"],
                fadeScreen=0.6,
                command=self.salir_programa
            )
            self.dialogo_salir.show()
        elif seleccion == "insertar_start_meta" and condiciones_extra:
            self.cuadro_ingreso_numero_drones()
            # self.cuadro_ingreso_coordenadas()
        elif seleccion == "calcular_trayectorias" and condiciones_extra:
            self.dialogo_ejecutar_algoritmo = OkCancelDialog(
                text="¿Desea calcular las trayectorias?",
                buttonTextList=["Aceptar", "Cancelar"],
                fadeScreen=0.6,
                command=self.calcular_trayectorias
            )
            self.dialogo_ejecutar_algoritmo.show()
        elif seleccion == "guardar_trayectorias" and condiciones_extra:
            self.dialogo_guardar_trayectorias = OkCancelDialog(
                text="¿Desea guardar las trayectorias?",
                buttonTextList=["Aceptar", "Cancelar"],
                fadeScreen=0.6,
                command=self.guardar_trayectorias
            )
            self.dialogo_guardar_trayectorias.show()

    def salir_programa(self, args):
        self.dialogo_salir.hide()
        self.dialogo_salir.destroy()
        self.dialogo_salir = None
        if args == 1:
            # self.eliminar_objetos_pantalla()
            sys.exit()

    def cuadro_ingreso_numero_drones(self):
        self.dialogo_numero_drones = DirectDialog(
            frameSize=(-0.50, 0.50, -0.40, 0.40),
            fadeScreen=0.6,
        )
        DirectLabel(
            text="Ingrese el número de drones",
            scale=0.07,
            pos=(0, 0, 0.30),
            parent=self.dialogo_numero_drones
        )
        entrada_numero_drones = DirectEntry(
            frameColor=(1, 1, 1, 1),
            scale=0.07,
            width=4,
            numLines=1,
            suppressKeys=1,
            suppressMouse=1,
            pos=(-0.125, 0, 0),
            parent=self.dialogo_numero_drones
        )
        numero_drones = entrada_numero_drones
        DirectButton(
            text="Aceptar",
            scale=0.07,
            pos=(-0.25, 0, -0.25),
            command=self.cuadro_ingreso_coordenadas,
            extraArgs=[numero_drones],
            parent=self.dialogo_numero_drones
        )
        DirectButton(
            text="Cancelar",
            scale=0.07,
            pos=(0.25, 0, -0.25),
            command=self.eliminar_ingreso_numero_drones,
            parent=self.dialogo_numero_drones
        )
        self.dialogo_numero_drones.show()

    def eliminar_ingreso_numero_drones(self):
        self.dialogo_numero_drones.hide()
        self.dialogo_numero_drones.destroy()
        self.dialogo_numero_drones = None

    def cuadro_ingreso_coordenadas(self, numero_drones):
        try:
            numero = numero_drones.get()
            numero_drones = numero
            self.eliminar_ingreso_numero_drones()
        except:
            pass
        try:
            numero_drones = int(numero_drones)
            if numero_drones < 4:
                self.numero_drones = numero_drones
            else:
                self.numero_drones = 4
        except:
            print("Error en los datos ingresados")
            self.numero_drones = 4

        lista_coordenadas = []  # Lista que almacenará las coordenadas ingresadas
        self.dialogo_ingresar_coordenadas = DirectDialog(
            frameSize=(-0.90, 0.90, -0.70, 0.70),
            fadeScreen=0.6,
        )
        DirectLabel(
            text="Ingrese las coordenadas para cada uno de los drones",
            scale=0.07,
            pos=(0, 0, 0.60),
            parent=self.dialogo_ingresar_coordenadas
        )
        DirectLabel(
            text="Start",
            scale=0.07,
            pos=(0.23, 0, 0.50),
            parent=self.dialogo_ingresar_coordenadas
        )
        DirectLabel(
            text="Meta",
            scale=0.07,
            pos=(0.63, 0, 0.50),
            parent=self.dialogo_ingresar_coordenadas
        )
        DirectLabel(
            text="* Las coordenadas del Start y la Meta deben expresarse entre paréntesis.\n"
                 "Ejemplo: (0, 0, 0)",
            scale=0.05,
            pos=(0, 0, -0.40),
            parent=self.dialogo_ingresar_coordenadas
        )
        DirectButton(
            text="Aceptar",
            scale=0.07,
            pos=(-0.25, 0, -0.60),
            command=self.establecer_coordenadas,
            extraArgs=[lista_coordenadas],
            parent=self.dialogo_ingresar_coordenadas
        )
        DirectButton(
            text="Cancelar",
            scale=0.07,
            pos=(0.25, 0, -0.60),
            command=self.eliminar_ingreso_coordenadas,
            parent=self.dialogo_ingresar_coordenadas
        )
        posicion_labels = 0.35
        for i in range(self.numero_drones):
            DirectLabel(
                text="Coordenadas del drone %s:" % str(i + 1),
                scale=0.07,
                pos=(-0.40, 0, posicion_labels),
                parent=self.dialogo_ingresar_coordenadas
            )
            posicion_labels -= 0.19

        # Agregando los recuadros para la entrada de texto
        posicion_fila = 0.35
        numero_coordenadas = None
        for fila in range(self.numero_drones):
            posicion_columna = 0.10
            coordenadas = []
            for columna in range(2):
                entrada_coordenada = DirectEntry(
                    frameColor=(1, 1, 1, 1),
                    scale=0.07,
                    width=4,
                    numLines=1,
                    suppressKeys=1,
                    suppressMouse=1,
                    pos=(posicion_columna, 0, posicion_fila),
                    parent=self.dialogo_ingresar_coordenadas
                )
                # Si existen datos en las coordenadas de Start y Meta del constructor de la clase,
                # se agregarán a los recuadros como referencia
                if self.coordenadas_start is not None and self.coordenadas_meta is not None:
                    # Se restará 1 en la coordenada Z, debido a que las coordenadas del constructor
                    # están referenciadas a partir de la coordenada (0, 0, 1)
                    # *Dirigirse a la función validar_coordenadas para mayor información
                    if fila == 0:
                        numero_coordenadas = len(self.coordenadas_start)
                    if fila < numero_coordenadas:
                        if columna == 0:
                            coordenada_start = np.array(self.coordenadas_start[fila]) - np.array([0, 0, 1])
                            entrada_coordenada.enterText(str(tuple(coordenada_start)))
                        else:
                            coordenada_meta = np.array(self.coordenadas_meta[fila]) - np.array([0, 0, 1])
                            entrada_coordenada.enterText(str(tuple(coordenada_meta)))

                coordenadas.append(entrada_coordenada)
                posicion_columna += 0.40
            posicion_fila -= 0.19
            lista_coordenadas.append(coordenadas)
        self.dialogo_ingresar_coordenadas.show()

    def eliminar_ingreso_coordenadas(self):
        self.dialogo_ingresar_coordenadas.hide()
        self.dialogo_ingresar_coordenadas.destroy()
        self.dialogo_ingresar_coordenadas = None

    def cuadro_advertencia_coordenadas(self, advertencia):
        self.dialogo_ingresar_coordenadas.hide()    # Escondiendo el diálogo de ingreso de coordenadas
        self.dialogo_advertencia_coordenadas = OkDialog(
            text=advertencia,
            buttonTextList=["Aceptar"],
            fadeScreen=0.6,
            command=self.eliminar_advertencia_coordenadas
        )
        self.dialogo_advertencia_coordenadas.show()

    def eliminar_advertencia_coordenadas(self, args):
        if args:
            self.dialogo_advertencia_coordenadas.hide()
            self.dialogo_advertencia_coordenadas.destroy()
            self.dialogo_advertencia_coordenadas = None
        # Habilitando el diálogo de ingreso de coordenadas
        self.dialogo_ingresar_coordenadas.show()

    def cuadro_advertencia_algoritmo(self, advertencia):
        self.dialogo_advertencia_algoritmo = OkDialog(
            text=advertencia,
            buttonTextList=["Aceptar"],
            fadeScreen=0.6,
            command=self.eliminar_advertencia_algoritmo
        )
        self.dialogo_advertencia_algoritmo.show()

    def eliminar_advertencia_algoritmo(self, args):
        if args:
            self.dialogo_advertencia_algoritmo.hide()
            self.dialogo_advertencia_algoritmo.destroy()
            self.dialogo_advertencia_algoritmo = None

        # Estableciendo en False la bandera para habilitar las opciones del menú
        self.ejecucion_algoritmo = False

        # Abriendo el cuadro de ingreso de coordenadas, para informar al usuario que debe llenar dichos parámetros
        # antes de ejecutar cualquier acción
        self.cuadro_ingreso_coordenadas(self.numero_drones)

    def cuadro_advertencia_comando(self, advertencia):
        self.dialogo_advertencia_comando = OkDialog(
            text=advertencia,
            buttonTextList=["Aceptar"],
            fadeScreen=0.6,
            command=self.eliminar_advertencia_comando
        )
        self.dialogo_advertencia_comando.show()

    def eliminar_advertencia_comando(self, args):
        if args:
            self.dialogo_advertencia_comando.hide()
            self.dialogo_advertencia_comando.destroy()
            self.dialogo_advertencia_comando = None
            self.proceso_guardado = False

    def establecer_coordenadas(self, coordenadas):
        coordenadas_start = []
        coordenadas_meta = []
        for coordenada in coordenadas:
            # Obteniendo el texto
            coordenada_start = coordenada[0].get()
            coordenada_meta = coordenada[1].get()
            try:
                # Evaluando la cadena de texto
                coordenada_start = eval(coordenada_start)
                coordenada_meta = eval(coordenada_meta)
            except:
                break
            # Verificando si la evaluación dió como resultado una tupla o una lista
            condicion1 = type(coordenada_start) is tuple or type(coordenada_start) is list
            condicion2 = type(coordenada_meta) is tuple or type(coordenada_meta) is list
            if condicion1 and condicion2:
                # Comprobando el número de elementos
                elementos_coordenada_start = len(coordenada_start)
                elementos_coordenda_meta = len(coordenada_meta)
                if elementos_coordenada_start == 3 and elementos_coordenda_meta == 3:
                    try:
                        # Transformando los valores de las coordenadas a números enteros
                        # En caso que el valor no sea un número, saltará la excepción
                        coordenada_start = tuple(map(int, coordenada_start))
                        coordenada_meta = tuple(map(int, coordenada_meta))
                        # Agregando las coordenadas a la lista
                        coordenadas_start.append(tuple(coordenada_start))
                        coordenadas_meta.append(tuple(coordenada_meta))
                    except:
                        break
                else:
                    break
            else:
                break
        # Verifica si existen coordenadas para el Start y la Meta
        if coordenadas_start and coordenadas_meta:
            elementos_coordenadas_start = len(coordenadas_start)
            elementos_coordenadas_meta = len(coordenadas_meta)
            # El número de coordenadas para el Start y la Meta deben corresponder al número de drones
            if elementos_coordenadas_start == self.numero_drones and elementos_coordenadas_meta == self.numero_drones:
                # Validando las coordenadas obtenidas de las entradas de texto
                coordenadas_start_validadas, coordenadas_meta_validadas, no_validado = \
                    self.validar_coordenadas(coordenadas_start, coordenadas_meta)
                # Si existen elementos no validados se procede a indicarlos
                if no_validado is not None:
                    advertencia1 = "La coordenada %s del drone %s se encuentra dentro de un obstáculo"
                    advertencia2 = "En el drone %s hay coordenadas que se encuentran fuera del límite del entorno"
                    if no_validado[0] != "Fuera limite":
                        advertencia = advertencia1 % (no_validado[0], no_validado[1])
                    else:
                        advertencia = advertencia2 % no_validado[1]
                    self.cuadro_advertencia_coordenadas(advertencia)
                else:
                    # Eliminando el cuadro de ingreso de las coordenadas
                    self.eliminar_ingreso_coordenadas()
                    # Agregando las coordenadas validadas en el Start y la Meta
                    self.coordenadas_start = coordenadas_start_validadas
                    self.coordenadas_meta = coordenadas_meta_validadas
                    # Insertando las coordenadas del Start y la Meta en el entorno
                    marcador = "Mission Pad"
                    entorno_modificado = self.insertar_start_meta(marcador, coordenadas_start, coordenadas_meta)
                    # Configurando el algortimo A*
                    self.algoritmo = AStar3DSwarm(entorno_modificado, self.dimensiones_voxel, self.coordenadas_start,
                                                  self.coordenadas_meta)
            else:
                self.cuadro_advertencia_coordenadas("Datos inválidos")
        else:
            self.cuadro_advertencia_coordenadas("Datos inválidos")

    def validar_coordenadas(self, coordenadas_start, coordenadas_meta):
        # Límites del entorno
        limite_x, limite_y, limite_z = self.entorno.shape
        # Indica el número de drone al que no se le pudo validar la coordenada ingresada por el usuario
        no_validado = None
        for indice in range(len(coordenadas_start)):
            start_x, start_y, start_z = coordenadas_start[indice]
            meta_x, meta_y, meta_z = coordenadas_meta[indice]
            # Verificando si las coordenadas del Start y la Meta contienen valores positivos y están dentro de los
            # límites del entorno
            condicion_start = (start_x >= 0 and start_y >= 0 and start_z >= 0) and \
                              (start_x <= limite_x - 1 and start_y <= limite_y - 1 and start_z <= limite_z - 1)
            condicion_meta = (meta_x >= 0 and meta_y >= 0 and meta_z >= 0) and \
                             (meta_x <= limite_x - 1 and meta_y <= limite_y - 1 and meta_z <= limite_z - 1)
            if condicion_start and condicion_meta:
                # Verificando si las coordenadas del Start y la Meta se encuentran fuera de un obstáculo
                coordenada_start = coordenadas_start[indice]
                coordenada_meta = coordenadas_meta[indice]
                # Convirtiendo las coordenadas del Start y la Meta a valores válidos para el análisis del algoritmo
                # En dichas coordenadas se incrementará en 1 el valor de Z, porque la posición designada para el
                # origen se encuentra sobre la plataforma en las coordenadas (0, 0, 1)
                coordenada_start = np.array(coordenada_start) + np.array([0, 0, 1])
                coordenada_meta = np.array(coordenada_meta) + np.array([0, 0, 1])
                if not self.entorno[tuple(coordenada_start)]:
                    coordenadas_start[indice] = tuple(coordenada_start)
                else:
                    no_validado = ("Start", indice + 1)
                    break
                if not self.entorno[tuple(coordenada_meta)]:
                    coordenadas_meta[indice] = tuple(coordenada_meta)
                else:
                    no_validado = ("Meta", indice + 1)
                    break
            else:
                no_validado = ("Fuera limite", indice + 1)
                break
        return coordenadas_start, coordenadas_meta, no_validado

    def construir_entorno(self):
        dx, dy, dz = self.dimensiones_voxel
        n_filas, n_columnas, n_niveles = self.entorno.shape
        # Construyendo el entorno
        for x in range(n_filas):
            for y in range(n_columnas):
                for z in range(n_niveles):
                    if self.entorno[x, y, z]:
                        tipo_elemento = self.objetos[x, y, z]
                        clase = tipo_elemento[0]    # Tipo de objeto ya sea Voxel o VoxelMap
                        textura = tipo_elemento[1]  # Textura del objeto
                        posicion = (x * dx, y * dy, z * dz)
                        if clase == 0:
                            Voxel(posicion=posicion, escala=tuple(self.dimensiones_voxel), textura=textura,
                                  parent=self.nodo_entorno)
                        else:
                            VoxelMap(posicion=posicion, escala=tuple(self.dimensiones_voxel), textura=textura,
                                     parent=self.nodo_entorno)

    def insertar_start_meta(self, marcador, coordenadas_start, coordenadas_meta):
        self.borrar_start_meta()    # Borrando los elementos agregados previamente

        iteraciones = len(coordenadas_start)
        factor_escala = self.dimensiones_voxel
        entorno_modificado = copy.deepcopy(self.entorno)
        for i in range(iteraciones):
            # Verifica si existe un voxel para apoyar el marcador
            # Si no es así, crea un voxel para tal fin
            # Para ello se disminuye en 1 el valor de Z de las coordenadas de Start y Meta, para comprobar la existencia
            # o no de un voxel por debajo de las coordenadas propuestas, y con ello posicionar adecuadamente el marcador
            start = np.array(coordenadas_start[i]) - np.array([0, 0, 1])
            meta = np.array(coordenadas_meta[i]) - np.array([0, 0, 1])
            if not self.entorno[tuple(start)]:
                entorno_modificado[tuple(start)] = True
                posicion_start = start * factor_escala
                Voxel(posicion=tuple(posicion_start), escala=tuple(factor_escala), parent=self.nodo_start_meta)
            if not self.entorno[tuple(meta)]:
                entorno_modificado[tuple(meta)] = True
                posicion_meta = meta * factor_escala
                Voxel(posicion=tuple(posicion_meta), escala=tuple(factor_escala), parent=self.nodo_start_meta)

            # Posicionando los marcadores en el lugar solicitado
            posicion_start = (start * factor_escala) + np.array([0, 0, (factor_escala[2] / 2) + 0.01])
            posicion_meta = (meta * factor_escala) + np.array([0, 0, (factor_escala[2] / 2) + 0.01])

            posicion_start = tuple(posicion_start)
            posicion_meta = tuple(posicion_meta)
            escala = tuple(factor_escala)
            orientacion = (-90, 0, 0)

            if marcador == "Mission Pad":
                # Mission Pad Start
                MissionPad(identificador=i+1, posicion=posicion_start, orientacion=orientacion, escala=escala,
                           parent=self.nodo_start_meta)
                # Mission Pad Meta
                MissionPad(identificador=i+1, posicion=posicion_meta, orientacion=orientacion, escala=escala,
                           parent=self.nodo_start_meta)
            elif marcador == "Aruco Marker":
                # Aruco Marker Start
                ArucoMarker(identificador=i, posicion=posicion_start, orientacion=orientacion, escala=escala,
                            parent=self.nodo_start_meta)
                # Aruco Marker Meta
                ArucoMarker(identificador=i, posicion=posicion_meta, orientacion=orientacion, escala=escala,
                            parent=self.nodo_start_meta)

        return entorno_modificado

    def borrar_start_meta(self):
        for elemento in self.nodo_start_meta.getChildren():
            elemento.detachNode()
            elemento.removeNode()

    def calcular_trayectorias(self, args):
        self.dialogo_ejecutar_algoritmo.hide()
        self.dialogo_ejecutar_algoritmo.destroy()
        self.dialogo_ejecutar_algoritmo = None
        if args == 1:
            self.ejecucion_algoritmo = True
            if self.coordenadas_start is not None and self.coordenadas_meta is not None:
                _, self.trayectorias_referenciales, self.trayectorias_reales, registro_drones = \
                    self.algoritmo.ejecutar()
                # Si existen trayectorias que no se pudieron calcular para los drones presentes en el registro
                # se muestra la advertencia respectiva
                if registro_drones:
                    advertencia = "No se pudo determinar una trayectoria libre de colisiones para los drones:\n"
                    drones = ""
                    for drone in registro_drones:
                        drones += str(drone) + ", "
                    self.cuadro_advertencia_algoritmo(advertencia + drones)

                # Dibujando las trayectorias
                colores = [(0, 128, 255, 1), (255, 128, 64, 1), (128, 0, 64, 1), (128, 255, 128, 1)]
                self.dibujar_trayectorias(self.trayectorias_referenciales, colores)
                self.ejecucion_algoritmo = False
            else:
                self.cuadro_advertencia_algoritmo("No existen datos para la ejecución del algoritmo")

    def dibujar_trayectorias(self, trayectorias, colores):
        self.borrar_trayectorias()  # Borrando las líneas dibujadas, si existe alguna
        # Creando un node path para contener los segmentos de recta
        node_path = NodePath("nodo linea")
        for i, trayectoria in enumerate(trayectorias):
            linea = LineSegs()
            color = colores[i]
            rgb = Vec3(color[:-1]) * (1/255)
            rgba = Vec4(rgb[0], rgb[1], rgb[2], color[3])
            linea.setColor(rgba)
            linea.setThickness(4)
            for indice in range(len(trayectoria) - 1):
                linea.moveTo(Vec3(trayectoria[indice]))
                linea.drawTo(Vec3(trayectoria[indice + 1]))
            nodo_linea = linea.create(False)
            node_path.attachNewNode(nodo_linea)
        node_path.reparentTo(self.nodo_trayectorias_dibujadas)

    def borrar_trayectorias(self):
        for elemento in self.nodo_trayectorias_dibujadas.getChildren():
            elemento.detachNode()
            elemento.removeNode()

    def guardar_trayectorias(self, args):
        self.dialogo_guardar_trayectorias.hide()
        self.dialogo_guardar_trayectorias.destroy()
        self.dialogo_guardar_trayectorias = None
        if args == 1:
            self.proceso_guardado = True
            if self.trayectorias_reales is not None:
                respuesta = guardar_trayectorias(self.trayectorias_reales, self.nombre_directorio)
                if respuesta:
                    mensaje = "Guardado correctamente"
                else:
                    mensaje = "No se puede guardar un archivo que ya existe"
                self.dialogo_respuesta_guardado(mensaje)
            else:
                advertencia = "No existe ninguna trayectoria"
                self.cuadro_advertencia_comando(advertencia)

    def dialogo_respuesta_guardado(self, advertencia):
        self.dialogo_respuesta_guardar_trayectorias = OkDialog(
            text=advertencia,
            buttonTextList=["Aceptar"],
            fadeScreen=0.6,
            command=self.eliminar_dialogo_respuesta_guardado
        )
        self.dialogo_respuesta_guardar_trayectorias.show()

    def eliminar_dialogo_respuesta_guardado(self, args):
        if args:
            self.dialogo_respuesta_guardar_trayectorias.hide()
            self.dialogo_respuesta_guardar_trayectorias.destroy()
            self.dialogo_respuesta_guardar_trayectorias = None

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

        # Eliminando todos los objetos vinculados al render
        for nodo in self.render.getChildren():
            nodo.removeNode()

        # Removiendo las tareas e ignorando todos los eventos
        self.taskMgr.remove("update")
        self.ignoreAll()


def abrir_entorno(nombre_directorio):
    ruta = "../Entornos/Entornos3D/Archivos/" + nombre_directorio
    matriz_base = leer_matriz(ruta + "/matriz_base.npy")
    matriz_objetos = leer_matriz(ruta + "/matriz_objetos.npy")
    dimensiones_voxel = leer_matriz(ruta + "/dimensiones_voxel.npy")
    dimensiones_entorno = leer_matriz(ruta + "/dimensiones_entorno.npy")
    return [matriz_base, matriz_objetos, dimensiones_voxel, dimensiones_entorno]


def guardar_trayectorias(trayectorias, nombre_directorio):
    ruta = "../Trayectorias3D/" + nombre_directorio
    # Creando un directorio para alojar los archivos
    respuesta = crear_directorio(ruta)
    if respuesta:
        guardar_matriz(trayectorias, ruta + "/trayectorias")
    return respuesta
