import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from Planning2D.Entornos.EntornosCuadriculados import entorno1
from Algoritmos.Algoritmos2D_Animacion import grassfire
from matplotlib.animation import FuncAnimation

# Se utiliza para visualizar el gráfico en una ventana flotante y no en la ventana del IDE
mpl.use('Qt5Agg')
# Esta configuración aumenta la calidad de imagen durante el proceso de guardado
mpl.rcParams['savefig.dpi'] = 1200

fig = plt.figure(constrained_layout=True)
fig.canvas.set_window_title("Algoritmo Grassfire")
ax = fig.add_subplot(1, 1, 1)

# Configuración e inicialización del entorno
start = (1, 1)  # Ubicación del nodo Start
meta = (10, 10)   # Ubicación del nodo Meta
base, representacion = entorno1.entorno(start=start, meta=meta)

# Llamada y configuración inicial del algoritmo Grassfire
algoritmo_grassfire = grassfire.Grassfire2D()
algoritmo_grassfire.configurar(entorno=base, start=start, meta=meta)

# Graficando el entorno base
cuadriculas = ax.imshow(representacion, interpolation="nearest", origin="upper",
                        extent=(0, base.shape[1], base.shape[0], 0), aspect="equal")

# Configuración del aspecto gráfico
# Título del gráfico
# ax.set_title("Algoritmo Grassfire", fontweight="bold", loc="center")

# Definiendo los límites del gráfico
ax.set_xlim(0, base.shape[1])
ax.set_ylim(base.shape[0], 0)

# Estableciendo los ticks en el gráfico
ax.set_xticks(np.arange(0, base.shape[1] + 1, 1))
ax.set_xticklabels([])  # Elimina los labels de los ticks en el eje X
ax.set_yticks(np.arange(0, base.shape[0] + 1, 1))
ax.set_yticklabels([])  # Elimina los labels de los ticks en el eje Y

# Añadiendo ticks intermedios en el gráfico
ax.set_xticks(np.arange(0.5, base.shape[1], 1), minor=True)
ax.set_xticklabels(np.arange(0, base.shape[1], 1), minor=True)     # Agregando labels a los ticks en X
ax.set_yticks(np.arange(0.5, base.shape[0], 1), minor=True)
ax.set_yticklabels(np.arange(0, base.shape[0], 1), minor=True)     # Agregando labels a los ticks en Y
ax.tick_params(axis="both", which="minor", length=0)   # Estableciendo la longitud de los minor ticks a cero

# Dibujando la grilla
ax.grid(visible=True, color="white", linewidth=1.5, animated=True)


def update(datos):
    etiqueta = datos[0]
    if etiqueta is not None:
        nodo = datos[1]
        if etiqueta == "visitado":
            distancia = datos[2]
            if nodo != meta and nodo != start:
                representacion[nodo] = [0, 128, 255]
                cuadriculas.set_data(representacion)
                # Indicando las distancias de cada cuadricula
                # Para aumentar la velocidad de animación eliminar la siguiente línea
                ax.text(nodo[1] + 0.5, nodo[0] + 0.5, distancia, ha="center", va="center", color="k")
            else:
                # Indicando las distancias de cada cuadricula
                # Para aumentar la velocidad de animación eliminar la siguiente línea
                ax.text(nodo[1] + 0.5, nodo[0] + 0.5, distancia, ha="center", va="center", color="k")
        else:
            # Indicando la trayectoria
            nodo_trayectoria = nodo
            if nodo_trayectoria == start or nodo_trayectoria == meta:
                pass
                # representacion[nodo_trayectoria] = [255, 127, 39]
                # cuadriculas.set_data(representacion)
            else:
                representacion[nodo_trayectoria] = [255, 128, 0]
                cuadriculas.set_data(representacion)
                plt.pause(0.01)

    return cuadriculas,


animacion = FuncAnimation(fig, update, frames=algoritmo_grassfire.ejecutar(), interval=10, blit=False, repeat=False)
plt.show()
