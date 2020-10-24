import logging
import socket
from threading import Thread


class Servidor:
    # Configuración de un logging para la presentación de la información de estado del drone
    logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.NOTSET)

    def __init__(self):
        # Asociando la dirección de estado con su puerto respectivo
        self.local_address_estado = ("", 8890)

        # Especificando un socket para la recepción de la información de estado de los drones
        self.socket_estado = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Configurando el socket de estado
        self.socket_estado.bind(self.local_address_estado)

        # Mantiene un registro actualizado sobre la información de estado de todos los drones
        self.registros_estado = {}

        # Creando y ejecutando un hilo para la recepción de la información de estado
        self.hilo_recepcion = Thread(target=self.servidor)
        self.hilo_recepcion.daemon = True
        self.hilo_recepcion.start()

    def servidor(self):
        while True:
            try:
                informacion_estado, drone_address = self.socket_estado.recvfrom(1024)
                informacion_estado = informacion_estado.decode(encoding="UTF-8")
                self.registros_estado[drone_address[0]] = informacion_estado
                # logging.info("%s: %s" % (drone_address[0], informacion_estado))
            except Exception as e:
                logging.error("Problemas en la recepción del estado: %s" % str(e), exc_info=True)