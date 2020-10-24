import socket


def set_ap(ssid, password):
    """
    Función para establecer el Tello Drone en modo AP
    :param ssid: El ssid de la red (nombre de la red Wifi)
    :param password: Contraseña de la red
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket para enviar los comandos
    my_socket.bind(("", 8889))
    cmd_str = "command"
    print("Enviando comando %s" % cmd_str)
    my_socket.sendto(cmd_str.encode("utf-8"), ("192.168.10.1", 8889))
    response, ip = my_socket.recvfrom(100)
    print("de %s: %s" % (ip, response))

    cmd_str = "ap %s %s" % (ssid, password)
    print("Enviando comando %s" % cmd_str)
    my_socket.sendto(cmd_str.encode("utf-8"), ("192.168.10.1", 8889))
    response, ip = my_socket.recvfrom(100)
    print("de %s: %s" % (ip, response))


# Configuración del Tello EDU en modo AP
# Funciona solamente si el computador que realizará la configuración está conectado a través de WiFi al Tello EDU
set_ap("Swarm-Tello", "1234")
