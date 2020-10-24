from threading import Thread
import time


class Supervisor:
    def __init__(self, ip_drone, servidor):
        # Dirección IP del drone
        self.ip_drone = ip_drone

        # Guarda información actualizada sobre el estado del drone
        self.estado_drone = {}

        # Instancia del servidor principal
        self.servidor = servidor

        # Creando y ejecutando un hilo para la recepción de la información de estado del drone
        self.hilo_informacion = Thread(target=self.informacion_estado)
        self.hilo_informacion.daemon = True
        self.hilo_informacion.start()

    def informacion_estado(self):
        while True:
            if self.ip_drone in self.servidor.registros_estado:
                estado = self.servidor.registros_estado[self.ip_drone]
                self.estado_drone = reestructurar_informacion(estado)

            time.sleep(0.01)    # Tiempo de espera para no sobrecargar la CPU

    def obtener_informacion(self, clave):
        valor = None
        if clave in self.estado_drone:
            valor = int(float(self.estado_drone[clave]))
        return valor

    # Número de mission pad (1 al 8). Si no se detecta el mission pad, el valor entregado es de -1.
    def id_mission_pad(self):
        return self.obtener_informacion("mid")

    # Posición X, Y, Z relativa al mission pad. Las unidades entregadas se miden en centímetros.
    def posicion(self):
        x = self.obtener_informacion("x")
        y = self.obtener_informacion("y")
        z = self.obtener_informacion("z")
        return [x, y, z]

    # Altura del drone medida en centímetros
    def altura(self):
        tof = self.obtener_informacion("tof")   # Altura relativa obtenida através del sensor tof
        h = self.obtener_informacion("h")       # Altura relativa respecto al último movimiento vertical
        return [tof, h]

    # Actitud del drone medida en grados
    def actitud(self):
        roll = self.obtener_informacion("roll")
        pitch = self.obtener_informacion("pitch")
        yaw = self.obtener_informacion("yaw")
        return [roll, pitch, yaw]

    # Velocidad del drone (cm/s) con respecto a los ejes coordenados X, Y, Z
    def velocidad(self):
        vx = self.obtener_informacion("vgx")
        vy = self.obtener_informacion("vgy")
        vz = self.obtener_informacion("vgz")
        return [vx, vy, vz]

    # Aceleración del drone (cm/s^2) respecto a los ejes coordenados X, Y, Z
    def aceleracion(self):
        ax = self.obtener_informacion("agx")
        ay = self.obtener_informacion("agy")
        az = self.obtener_informacion("agz")
        return [ax, ay, az]

    # Porcentaje de batería del drone
    def bateria(self):
        return self.obtener_informacion("bat")


# Reestructura la información de estado del drone convirtiendola en un diccionario para facilitar el
# acceso a los datos
def reestructurar_informacion(estado):
    informacion = estado
    # Eliminando los espacios en blanco al inicio y al final de la cadena
    informacion = informacion.strip()
    # Transformando la cadena en una lista
    informacion = informacion.split(";")
    # Llenando el diccionario de estado
    diccionario_estado = {}
    for dato in informacion:
        if dato:
            v = dato.split(":")
            if len(v) < 2:
                continue
            clave = v[0]
            valor = v[1]
            diccionario_estado[clave] = valor
    return diccionario_estado
