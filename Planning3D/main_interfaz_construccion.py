from Planning3D.interfaz_construccion import InterfazConstruccion
from Planning3D.interfaz_construccion import calculo_rendimiento


def main():
    dimensiones_entorno = (4, 4, 4)
    dimensiones_voxel = (0.5, 0.5, 0.5)
    nmax_voxels_iniciales = 10
    respuesta = calculo_rendimiento(dimensiones_entorno, dimensiones_voxel)
    if respuesta:
        app = InterfazConstruccion(dimensiones_entorno, dimensiones_voxel, nmax_voxels_iniciales)
        app.run()


if __name__ == "__main__":
    main()
