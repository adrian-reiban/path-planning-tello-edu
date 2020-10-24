from os import scandir


def listar_ficheros(ruta):
    contenido = None
    try:
        contenido = [obj.name for obj in scandir(ruta) if obj.is_file()]
    except Exception as e:
        print(e)
    return contenido


def listar_directorios(ruta):
    contenido = None
    try:
        contenido = [obj.name for obj in scandir(ruta) if obj.is_dir() and obj.name != "__pycache__"]
    except Exception as e:
        print(e)
    return contenido
