import numpy as np

COLOR_START = np.array([0, 255, 0])
COLOR_META = np.array([255, 0, 0])
COLOR_CELDA_LIBRE = np.array([195, 195, 195])
COLOR_OBSTACULO = np.array([0, 0, 0])


def entorno(start, meta):
    # Celda libre = 0
    # Celda con obstáculo = 1
    base = np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]])

    n_filas, n_columnas = base.shape
    representacion = np.zeros((n_filas, n_columnas, 3), np.int)
    representacion[start] = COLOR_START
    representacion[meta] = COLOR_META
    for i in range(n_filas):
        for j in range(n_columnas):
            if (i, j) != start and (i, j) != meta:
                if base[i, j] == 0:
                    representacion[i, j] = COLOR_CELDA_LIBRE
                else:
                    representacion[i, j] = COLOR_OBSTACULO
    return base, representacion
