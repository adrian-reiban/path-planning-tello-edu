from threading import Thread

from ControlDrone.visualizador import Visualizador
from ControlDrone.servidor import Servidor
from ControlDrone.supervisor import Supervisor
from ControlDrone.controlador import Controlador
from ControlDrone.tello import Tello


class CentralComando:
    IP_BASE = "192.168.100."
    PUERTO_LOCAL_BASE = 9000
    NOMBRE_BASE = "Tello"

    def __init__(self, nombre_entorno, trayectorias):
        # Nombre del entorno
        self.nombre_entorno = nombre_entorno
        # Contiene una lista de trayectorias únicas, definidas para cada drone
        self.trayectorias = trayectorias

        # Listas que contendrán los drones, sus direcciones IP, y los puertos de comunicación de la
        # computadora local
        self.nombre_drones = []
        self.lista_drones = []
        self.lista_controladores = []
        self.lista_supervisores = []

        # Servidor de escucha para la recepción de información de estado de los drones
        self.servidor = Servidor()

        # Visualizador de estado
        self.visualizador = None

        # Configuración inicial
        self.configuracion()

    def configuracion(self):
        numero_drones = len(self.trayectorias)
        # Construyendo e inicializando los objetos del tipo Supervisor, y Tello
        for indice in range(numero_drones):
            nombre_drone = self.NOMBRE_BASE + str(indice + 1)
            ip_drone = self.IP_BASE + str(indice + 11)
            puerto_local = self.PUERTO_LOCAL_BASE + indice
            drone = Tello(nombre_drone, ip_drone, puerto_local)
            supervisor = Supervisor(ip_drone, self.servidor)

            # Configurando el controlador
            id_mission_pad = indice + 1
            velocidad = 50
            trayectoria = self.trayectorias[indice]
            controlador = Controlador(drone, supervisor, id_mission_pad, velocidad, trayectoria)

            # Actualizando las listas de drones, supervisores y controladores
            self.nombre_drones.append(nombre_drone)
            self.lista_drones.append(drone)
            self.lista_supervisores.append(supervisor)
            self.lista_controladores.append(controlador)

    def iniciar(self):
        for controlador in self.lista_controladores:
            hilo = Thread(target=controlador.ejecutar)
            hilo.start()

        # Construyendo la ventana de visualizacion
        self.visualizador = Visualizador(self.nombre_entorno, self.nombre_drones, self.trayectorias,
                                         self.lista_supervisores)
        self.visualizador.showMaximized()
