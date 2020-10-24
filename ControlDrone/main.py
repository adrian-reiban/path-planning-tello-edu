import sys
from PyQt5.QtWidgets import QApplication
from ControlDrone.central_comando import CentralComando
from FuncionesGuardado.matrices import leer_matriz


def abrir_trayectorias(nombre_directorio):
    ruta = "../Trayectorias3D/" + nombre_directorio
    trayectorias = leer_matriz(ruta + "/trayectorias.npy")
    return trayectorias


def principal():
    nombre_directorio = "Entorno1"
    trayectorias = abrir_trayectorias(nombre_directorio)
    app = QApplication(sys.argv)
    central_comando = CentralComando(nombre_directorio, trayectorias)
    central_comando.iniciar()
    app.exec_()


if __name__ == "__main__":
    principal()
