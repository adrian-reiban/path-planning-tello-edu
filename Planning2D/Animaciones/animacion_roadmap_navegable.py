import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from Planning2D.Entornos.EntornosPoligonales.EntornosNavegables import entorno1
from Algoritmos.Algoritmos2D import roadmap, trapezoidacion

# Se utiliza para visualizar en una ventana flotante y no en la ventana del IDE
mpl.use("Qt5Agg")
# Esta configuración aumenta la calidad de imagen durante el proceso de guardado
mpl.rcParams['savefig.dpi'] = 1200

fig = plt.figure(constrained_layout=True)
fig.canvas.set_window_title("Algoritmo Trapezoidación - Roadmap")
ax = fig.add_subplot(1, 1, 1)

# Obteniendo los parámetros del entorno
limites_entorno, obstaculos, start, meta = entorno1.entorno()

# Configurando y ejecutando el algoritmo de Trapezoidación
algoritmo_trapezoidacion = trapezoidacion.Trapezoidacion(limites_entorno, obstaculos)
algoritmo_trapezoidacion.ejecutar()
# Obteniendo los resultados del algoritmo de Trapezoidación
limites_entorno_poligonal, lineas_divisorias, trapecios, fronteras_trapecios, fronteras_compartidas = \
    algoritmo_trapezoidacion.obtener_resultados()

# Configurando y ejecutando el algoritmo de Roadmap
algoritmo_roadmap = roadmap.RoadMap(trapecios, lineas_divisorias, fronteras_trapecios, fronteras_compartidas, start, meta)
centros_trapecios, centros_lineas, nodos_trayectoria, puntos_trayectoria = algoritmo_roadmap.ejecutar()

# Configurando el aspecto gráfico
# Título del gráfico
# ax.set_title("Algoritmo Trapezoidación - Roadmap", fontweight="bold", loc="center")

# Especificando los límites del gráfico
ax.set_xlim(limites_entorno_poligonal[0])
ax.set_ylim(limites_entorno_poligonal[1])

# Agregando los labels en el gráfico
ax.set_xlabel("X", labelpad=10, weight="bold")
ax.set_ylabel("Y", rotation="0", labelpad=10, weight="bold")

# Dibujando los obstáculos del entorno
for poligono in obstaculos:
    obstaculo = Polygon(poligono, closed=True)
    ax.add_patch(obstaculo)

# Insertando los puntos de Start y Meta
ax.scatter(start[0], start[1], s=80, marker="o", color="green", zorder=2.5)
ax.scatter(meta[0], meta[1], s=120, marker="*", color="red", zorder=2.5)


# Dibujando las regiones trapezoidales (nodos) del entorno
for indice, trapecio in enumerate(trapecios, 0):
    region = Polygon(trapecio, closed=True, color="silver", alpha=0.5)
    ax.add_patch(region)
    plt.pause(0.3)

# Numerando las regiones trapezoidales
for numero, centro in enumerate(centros_trapecios, 0):
    ax.text(centro[0], centro[1] + 10, numero, ha="center", va="center", color="k")
    plt.pause(0.3)

# Dibujando los centros de las regiones trapezoidales
for centro in centros_trapecios:
    ax.scatter(centro[0], centro[1], s=12, marker="D", edgecolors="black", color="white")
    plt.pause(0.3)


# Dibujando los centros de las lineas verticales que dividen las regiones trapezoidales del entorno
for centros in centros_lineas:
    for punto in centros:
        ax.scatter(punto[0], punto[1], s=15, marker="o", color="blue", zorder=2.5)
        plt.pause(0.3)

# Verifica si existen nodos de trayectoria para dibujarlos
if nodos_trayectoria is None:
    print("No se ha encontrado un camino hasta el objetivo")
else:
    # Indicando los nodos trayectoria
    for nodo in nodos_trayectoria:
        region = Polygon(trapecios[nodo], closed=True, color="red", alpha=0.2)
        ax.add_patch(region)
        plt.pause(0.3)

    # Dibujando la trayectoria
    for indice, camino in enumerate(puntos_trayectoria, 0):
        if indice < len(puntos_trayectoria) - 1:
            punto1 = camino
            punto2 = puntos_trayectoria[indice + 1]
            puntos_x = [punto1[0], punto2[0]]
            puntos_y = [punto1[1], punto2[1]]
            ax.plot(puntos_x, puntos_y, "-", linewidth=1.25, color="k")
            plt.pause(0.3)

plt.show()
