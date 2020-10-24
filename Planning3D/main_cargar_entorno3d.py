from Planning3D.cargar_entorno3d import CargarEntorno


def main():
    nombre_directorio = "Entorno1"
    # Ejecución del programa
    cargar_entorno = CargarEntorno(nombre_directorio)
    cargar_entorno.run()


if __name__ == "__main__":
    main()
