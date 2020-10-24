# Este programa se usa solamente para pruebas de testeo de comandos
from ControlDrone.tello import Tello

tello = Tello("Tello-Prueba", "192.168.10.1", 9000)
tello.enviar_mensaje_control("command")
tello.enviar_mensaje_control("battery?")
tello.enviar_mensaje_control("takeoff")
tello.enviar_mensaje_control("down 50")
tello.enviar_mensaje_control("forward 100")
tello.enviar_mensaje_control("up 50")
tello.enviar_mensaje_control("land")
