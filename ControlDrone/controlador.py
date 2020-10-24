import numpy as np


class Controlador:
    def __init__(self, drone, supervisor, id_mission_pad, velocidad, trayectoria):
        self.drone = drone
        self.supervisor = supervisor
        self.id_mission_pad = id_mission_pad
        self.velocidad = velocidad
        self.trayectoria = trayectoria

        # Vectores unitarios que representan los ejes del drone en X, Y, Z.
        # La disposición de los ejes del drone se basa en el sistema coordenado de la mano derecha; siendo el eje X
        # positivo la dirección en la que apunta la cámara frontal del drone.
        # Todos los desplazamientos y rotaciones del drone, se basan en el sistema global de referencia (el del suelo)
        self.vector_unitario_drone = np.array([1, 0, 0])     # Dirección actual en la que apunta el eje X del drone

    def iniciar_comunicacion(self):
        respuesta = self.drone.enviar_mensaje_control("command")
        return respuesta

    def establecer_velocidad(self):
        if self.velocidad < 10:
            self.velocidad = 10
        elif self.velocidad >= 100:
            self.velocidad = 70
        respuesta = self.drone.enviar_mensaje_control("speed %s" % self.velocidad)
        return respuesta

    def despegar(self):
        respuesta = self.drone.enviar_mensaje_control("takeoff")
        return respuesta

    def aterrizar(self):
        respuesta = self.drone.enviar_mensaje_control("land")
        return respuesta

    def habilitar_deteccion_mission_pad(self):
        respuesta = self.drone.enviar_mensaje_control("mon")
        # Habilitando la detección del mission pad empleando sólamente la cámara inferior
        if respuesta:
            self.drone.enviar_mensaje_control("mdirection 0")
        return respuesta

    def deshabilitar_deteccion_mission_pad(self):
        respuesta = self.drone.enviar_mensaje_control("moff")
        return respuesta

    def ejecutar(self):
        respuesta_funciones_inicio = False
        funciones_inicio = [self.iniciar_comunicacion, self.establecer_velocidad, self.despegar]
        # funciones_inicio = [self.iniciar_comunicacion]
        for funcion in funciones_inicio:
            respuesta_funciones_inicio = funcion()
            if not respuesta_funciones_inicio:
                break
        # Ejecutando la trayectoria
        if respuesta_funciones_inicio:
            numero_coordenadas = len(self.trayectoria)
            if numero_coordenadas >= 4:
                for indice in range(numero_coordenadas - 2):
                    coordenada1 = self.trayectoria[indice]
                    coordenada2 = self.trayectoria[indice + 1]
                    # Comprueba si es la primera ejecución para ajustar la altura del drone
                    if indice == 0:
                        respuesta_comandos = self.desplazar_drone(coordenada1, coordenada2, True)
                    else:
                        respuesta_comandos = self.desplazar_drone(coordenada1, coordenada2, False)
                    if not respuesta_comandos:
                        break
            else:
                for indice in range(numero_coordenadas - 1):
                    coordenada1 = self.trayectoria[indice]
                    coordenada2 = self.trayectoria[indice + 1]
                    # Comprueba si es la primera ejecución para ajustar la altura del drone
                    if indice == 0:
                        respuesta_comandos = self.desplazar_drone(coordenada1, coordenada2, True)
                    else:
                        respuesta_comandos = self.desplazar_drone(coordenada1, coordenada2, False)
                    if not respuesta_comandos:
                        break
        self.aterrizar()

    def desplazar_drone(self, coordenada1, coordenada2, movimiento_inicial):
        respuesta = False
        comandos = self.convertir_coordenadas(coordenada1, coordenada2, movimiento_inicial)
        for comando in comandos:
            respuesta = self.drone.enviar_mensaje_control(comando)
            if not respuesta:
                break
        return respuesta

    # Convierte las coordenadas suministradas en comandos de control
    def convertir_coordenadas(self, coordenada1, coordenada2, movimiento_inicial):
        punto1 = np.array(coordenada1)
        punto2 = np.array(coordenada2)
        desplazamiento = (punto2 - punto1) * 100    # Convirtiendo la medida a centímetros

        x, y, z = desplazamiento
        comandos = []
        angulo = 0
        if z == 0:
            magnitud_desplazamiento = np.linalg.norm(desplazamiento)
            vector_unitario_desplazamiento = desplazamiento / magnitud_desplazamiento
            producto_cruz = np.cross(self.vector_unitario_drone, vector_unitario_desplazamiento)

            # Calculando el ángulo entre los vectores
            if np.array_equal(producto_cruz, np.zeros(3)):
                if np.array_equal(vector_unitario_desplazamiento, -self.vector_unitario_drone):
                    angulo = np.pi
            else:
                angulo = np.arcsin((np.linalg.norm(producto_cruz)) / (np.linalg.norm(self.vector_unitario_drone) *
                                                                      np.linalg.norm(vector_unitario_desplazamiento)))

            # Verifica la dirección del producto cruz para establecer el signo del ángulo
            if producto_cruz[2] < 0:
                angulo = -angulo

            # Actualizando la dirección del vector unitario del drone
            if angulo != 0:
                matriz_rotacion = np.array([[np.cos(angulo), -np.sin(angulo), 0], [np.sin(angulo), np.cos(angulo), 0],
                                            [0, 0, 1]])
                self.vector_unitario_drone = (np.dot(matriz_rotacion, self.vector_unitario_drone)).astype(dtype=np.int)

            # Convirtiendo el ángulo en grados
            angulo = int(angulo * 180 / np.pi)
            if (magnitud_desplazamiento > 0) and (angulo == 0):
                comandos.append("forward " + str(int(magnitud_desplazamiento)))
            elif (magnitud_desplazamiento > 0) and (angulo > 0):
                comandos.append("ccw " + str(angulo))
                comandos.append("forward " + str(int(magnitud_desplazamiento)))
            elif (magnitud_desplazamiento > 0) and (angulo < 0):
                comandos.append("cw " + str(-angulo))
                comandos.append("forward " + str(int(magnitud_desplazamiento)))

        elif x == 0 and y == 0 and z != 0:
            if z < 0:
                comandos.append("down " + str(int(-z)))
            else:
                # Comprueba si es la primera ejecución para ajustar la altura del drone
                if movimiento_inicial:
                    comandos.append("up " + str(int(z - 80)))
                else:
                    comandos.append("up " + str(int(z)))

        return comandos
