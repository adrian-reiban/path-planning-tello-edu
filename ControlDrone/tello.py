import logging
import socket
import time
from threading import Thread


class Tello:
    # Configuración de un logging para la presentación de información por consola
    logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.NOTSET)

    # Constantes de control del tiempo
    TIEMPO_DE_RESPUESTA = 10    # Tiempo máximo de espera de la respuesta ante un comando enviado
    TIEMPO_ENTRE_COMANDOS = 1   # Tiempo de espera para el envío de un nuevo comando
    NUMERO_REENVIOS = 3         # Número máximo de reenvíos de un comando

    def __init__(self, nombre_drone, ip_drone, puerto_local):
        # Estableciendo el nombre del drone
        self.nombre_drone = nombre_drone

        # Dirección IP del drone
        self.ip_drone = ip_drone

        # Puerto local empleado para la recepción de mensajes del drone
        self.puerto_local = puerto_local

        # Asociando la direción IP del drone con su puerto de comunicación
        self.tello_address = (self.ip_drone, 8889)

        # Asociando la dirección de comunicación con su puerto respectivo
        self.local_address_comunicacion = ("", puerto_local)

        # Especificando un socket para el manejo de la comunicación con el drone (envío y recepción de comandos)
        self.socket_comunicacion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Configurando el socket de comunicación
        self.socket_comunicacion.bind(self.local_address_comunicacion)

        # Almacenará la respuesta del drone en función del comando enviado
        self.respuesta_comunicacion = None

        # Obteniendo el tiempo actual; será empleado para determinar el tiempo transcurrido entre envíos y
        # recepciones de mensajes
        self.tiempo_ultimo_comando_recibido = time.time()

        # Creando y ejecutando un hilo para la recepción de mensajes
        self.hilo_recepcion = Thread(target=self.recibir)
        self.hilo_recepcion.daemon = True
        self.hilo_recepcion.start()

    # Se encarga de enviar el mensaje suministrado.
    # Si la acción determinada por el comando se ejecuta satisfactoriamente, la respuesta retornada es True;
    # caso contrario, la respuesta es False
    def envio_con_respuesta(self, comando):
        tiempo_transcurrido = time.time() - self.tiempo_ultimo_comando_recibido
        if tiempo_transcurrido < self.TIEMPO_ENTRE_COMANDOS:
            time.sleep(tiempo_transcurrido)
        logging.info("Enviando mensaje al %s:" % self.nombre_drone + comando)
        self.socket_comunicacion.sendto(comando.encode(encoding="UTF-8"), self.tello_address)
        # Espera hasta recibir respuesta por parte del drone
        respuesta = False
        marca_tiempo = time.time()
        while self.respuesta_comunicacion is None:
            # Comprueba si el tiempo actual es mayor al tiempo de respuesta para salir del bucle
            if (time.time() - marca_tiempo) > self.TIEMPO_DE_RESPUESTA:
                logging.warning("Tiempo de espera excedido para el %s" % self.nombre_drone)
                break
            time.sleep(0.01)    # Tiempo de espera para no sobrecargar la CPU

        if self.respuesta_comunicacion == "ok" or self.respuesta_comunicacion == "OK":
            respuesta = True
        self.respuesta_comunicacion = None
        self.tiempo_ultimo_comando_recibido = time.time()
        return respuesta

    # Se encarga del envío de mensajes, de los que no se necesita recibir respuesta
    def envio_sin_respuesta(self, comando):
        logging.info("Enviando mensaje al %s:" % self.nombre_drone + comando)
        self.socket_comunicacion.sendto(comando.encode(encoding="UTF-8"), self.tello_address)

    # Envía el mensaje de control suministrado; en caso de que exista algún problema con la recepción del mensaje
    # procedee a reenviarlo
    def enviar_mensaje_control(self, comando):
        respuesta = False
        for envio in range(self.NUMERO_REENVIOS):
            respuesta = self.envio_con_respuesta(comando)
            if respuesta:
                break
        if not respuesta:
            logging.warning("Se ha perdido la comunicación con el %s:" % self.nombre_drone)
        return respuesta

    # Se encarga de recibir los mensajes de respuesta ante el comando enviado
    def recibir(self):
        while True:
            try:
                respuesta, drone_address = self.socket_comunicacion.recvfrom(1024)
                self.respuesta_comunicacion = respuesta.decode(encoding="UTF-8")
                logging.info("Mensaje recibido del %s:" % self.nombre_drone + self.respuesta_comunicacion)
            except Exception as e:
                logging.error("Problemas en la recepción del mensaje del %s:" % self.nombre_drone + str(e),
                              exc_info=True)

    # Cierra el socket de comunicación
    def cerrar_socket(self):
        self.socket_comunicacion.close()
        logging.info("Comunicación con el %s cerrada" % self.nombre_drone)
        logging.shutdown()

    # Datos generales del drone
    def __str__(self):
        return ("Los datos del drone son: " +
                "\n\t* Nombre del drone: %s" % self.nombre_drone +
                "\n\t* IP del drone y puerto: IP: %s Puerto: %s " % self.tello_address + "\n")
