import numpy as np
from panda3d.core import Vec3, Vec4
from Modelos.Procedural.voxel import Voxel
from Modelos.Procedural.voxel_map import VoxelMap
from FuncionesGuardado.matrices import (crear_directorio, guardar_matriz)


class ConstruirEntorno3D:
    def __init__(self, dimensiones_entorno, dimensiones_voxel, nmax_voxels_iniciales, parent):
        self.dimensiones_entorno = dimensiones_entorno
        self.dimensiones_voxel = dimensiones_voxel
        # Número inicial de voxels que contendrá la plataforma.
        # Se empleará esta condición para no sobrecargar la vista de la escena
        self.nmax_voxels_iniciales = nmax_voxels_iniciales
        # Nodo padre al cual se emparentarán los voxels del entorno
        self.parent = parent

        # Calculando el número de voxels necesarios para delimitar la estructura del entorno
        self.nvoxels_x, self.nvoxels_y, self.nvoxels_z = calcular_numero_voxels(self.dimensiones_entorno,
                                                                                self.dimensiones_voxel)

        # Definiendo la matriz que almacenará la estrutura del entorno
        self.matriz_base = np.zeros((self.nvoxels_x, self.nvoxels_y, self.nvoxels_z), dtype=bool)

        # Matriz que contendrá los nombres de los objetos agregados al entorno y sus texturas
        self.matriz_objetos = np.empty((self.nvoxels_x, self.nvoxels_y, self.nvoxels_z), dtype=object)

        # Lista que contendrá los voxels que se agregarán de forma procedural
        self.lista_voxels = []

        # Guarda el número de voxels que contiene el entorno en determinado momento
        self.numero_voxels = None

        # Construyendo la plataforma
        self.construir_plataforma()

    def construir_plataforma(self):
        dx, dy, dz = self.dimensiones_voxel
        contador = 0
        nvoxels_x = self.nvoxels_x
        nvoxels_y = self.nvoxels_y

        # Construyendo la plataforma en función del número maximo inicial de voxels permitidos para cada lado
        # de la plataforma
        # El usuario progresivamente añadirá o eliminará voxels dependiendo del tamaño del entorno
        if (nvoxels_x > self.nmax_voxels_iniciales) and (nvoxels_y > self.nmax_voxels_iniciales):
            nvoxels_x = self.nmax_voxels_iniciales
            nvoxels_y = self.nmax_voxels_iniciales
        elif (nvoxels_x > self.nmax_voxels_iniciales) and (nvoxels_y <= self.nmax_voxels_iniciales):
            nvoxels_x = self.nmax_voxels_iniciales
        elif (nvoxels_x <= self.nmax_voxels_iniciales) and (nvoxels_y > self.nmax_voxels_iniciales):
            nvoxels_y = self.nmax_voxels_iniciales

        # Guardando el número de voxels que se añadirán a la escena
        self.numero_voxels = (nvoxels_x * nvoxels_y) - 1

        # Construyendo la plataforma
        for x in range(nvoxels_x):
            for y in range(nvoxels_y):
                voxel = Voxel(posicion=(x * dx, y * dy, 0), escala=self.dimensiones_voxel, parent=self.parent)
                # Etiquetando el objeto
                voxel.voxel.setTag("voxel", str(contador))
                contador += 1

                self.lista_voxels.append(voxel)

                # Actualizando la matriz base
                self.matriz_base[x, y, 0] = True

                # Guardando los objetos que forman la plataforma con su respectiva textura
                # El primer valor de la tupla, representa la clase de objeto y el segundo su textura.
                # Existen 2 clases de objetos en el programa: Voxel, y VoxelMap. El primero contiene una textura
                # simple y el segundo una textura de tipo UV Map.
                self.matriz_objetos[x, y, 0] = (0, "tile")

    def seleccionar_voxel(self, identificador):
        voxel = self.lista_voxels[identificador]
        voxel.voxel.setColor(Vec4(0, 1, 0, 1))

    def deseleccionar_voxel(self, identificador):
        voxel = self.lista_voxels[identificador]
        if voxel is not None:
            voxel.voxel.clearColor()

    def agregar_voxel(self, tipo_elemento, identificador, normal):
        punto_colision = self.lista_voxels[identificador].voxel.getPos()

        normal_x, normal_y, normal_z = normal
        posicion = None
        if normal_z != 0 and normal_x == 0 and normal_y == 0:
            if normal_z > 0.0:
                posicion = punto_colision + Vec3(0, 0, self.dimensiones_voxel[2])
            elif normal_z < 0.0:
                posicion = punto_colision + Vec3(0, 0, -self.dimensiones_voxel[2])

        elif normal_y != 0 and normal_z == 0 and normal_x == 0:
            if normal_y > 0.0:
                posicion = punto_colision + Vec3(0, self.dimensiones_voxel[1], 0)
            elif normal_y < 0.0:
                posicion = punto_colision + Vec3(0, -self.dimensiones_voxel[1], 0)

        elif normal_x != 0 and normal_z == 0 and normal_y == 0:
            if normal_x > 0.0:
                posicion = punto_colision + Vec3(self.dimensiones_voxel[0], 0, 0)
            elif normal_x < 0.0:
                posicion = punto_colision + Vec3(-self.dimensiones_voxel[0], 0, 0)

        if posicion is not None:
            limite_x = self.dimensiones_voxel[0] * self.nvoxels_x
            limite_y = self.dimensiones_voxel[1] * self.nvoxels_y
            limite_z = self.dimensiones_voxel[2] * self.nvoxels_z

            posicion_x, posicion_y, posicion_z = posicion
            condicion1 = (posicion_x >= 0) and (posicion_x < limite_x)
            condicion2 = (posicion_y >= 0) and (posicion_y < limite_y)
            condicion3 = (posicion_z >= 0) and (posicion_z < limite_z)

            if condicion1 and condicion2 and condicion3:
                clase = tipo_elemento[0]    # Tipo de objeto ya sea Voxel o VoxelMap
                textura = tipo_elemento[1]  # Textura del objeto
                if clase == 0:
                    voxel = Voxel(posicion=posicion, escala=self.dimensiones_voxel, textura=textura,
                                  parent=self.parent)
                else:
                    voxel = VoxelMap(posicion=posicion, escala=self.dimensiones_voxel, textura=textura,
                                     parent=self.parent)

                # Etiquetando el objeto y agregando a la lista
                self.numero_voxels += 1
                voxel.voxel.setTag("voxel", str(self.numero_voxels))
                self.lista_voxels.append(voxel)

                # Actualizando la matriz base
                coordenada_x = int(posicion_x / self.dimensiones_voxel[0])
                coordenada_y = int(posicion_y / self.dimensiones_voxel[1])
                coordenada_z = int(posicion_z / self.dimensiones_voxel[2])
                coordenada = (coordenada_x, coordenada_y, coordenada_z)
                self.matriz_base[coordenada] = True
                self.matriz_objetos[coordenada] = tipo_elemento
            else:
                print("No se puede añadir más voxels al entorno")

    def eliminar_voxel(self, identificador):
        voxel = self.lista_voxels[identificador]
        punto_colision = voxel.voxel.getPos()
        voxel.voxel.clearTag("voxel")
        voxel.voxel.detachNode()
        voxel.voxel.removeNode()
        self.lista_voxels[identificador] = None

        # Actualizando la matriz base
        posicion_x, posicion_y, posicion_z = punto_colision
        coordenada_x = int(posicion_x / self.dimensiones_voxel[0])
        coordenada_y = int(posicion_y / self.dimensiones_voxel[1])
        coordenada_z = int(posicion_z / self.dimensiones_voxel[2])
        coordenada = (coordenada_x, coordenada_y, coordenada_z)
        self.matriz_base[coordenada] = False
        self.matriz_objetos[coordenada] = None

    def guardar_entorno(self, nombre_directorio):
        ruta = "../Entornos/Entornos3D/Archivos/" + nombre_directorio
        # Creando un directorio para alojar los archivos
        respuesta = crear_directorio(ruta)
        if respuesta:
            guardar_matriz(self.matriz_base, ruta + "/matriz_base")
            guardar_matriz(self.matriz_objetos, ruta + "/matriz_objetos")
            guardar_matriz(np.array(self.dimensiones_voxel), ruta + "/dimensiones_voxel")
            guardar_matriz(np.array(self.dimensiones_entorno), ruta + "/dimensiones_entorno")
        return respuesta


# Determina el número de voxels necesarios para construir el entorno base
def calcular_numero_voxels(dimensiones_entorno, dimensiones_voxel):
    nvoxels_x = int(dimensiones_entorno[0] / dimensiones_voxel[0])
    nvoxels_y = int(dimensiones_entorno[1] / dimensiones_voxel[1])
    nvoxels_z = int(dimensiones_entorno[2] / dimensiones_voxel[2])
    # Se incrementa en 1 el número de voxels en Z para tomar en cuenta la altura del entorno a partir
    # de la superficie superior de la plataforma
    return [nvoxels_x, nvoxels_y, nvoxels_z + 1]
