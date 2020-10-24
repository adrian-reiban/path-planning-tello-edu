from Planning2D.Entornos.EntornosCuadriculados import entorno1
from Algoritmos.Algoritmos2D.a_star import AStar2D
from PlanningPseudo3D.Cuadriculacion.representar_solucion import RepresentarSolucion

# Coordenadas de Start y Meta
start = (1, 1)  # Ubicación del nodo Start
meta = (10, 10)   # Ubicación del nodo Meta

# Obtención de los parámetros del entorno
entorno, _ = entorno1.entorno(start, meta)
# Configuración y ejecución del algoritmo Grassfire
algoritmo_a_star = AStar2D(entorno, start, meta)
trayectoria = algoritmo_a_star.ejecutar()

representacion = RepresentarSolucion(entorno=entorno, start=start, meta=meta, trayectoria=trayectoria,
                                     dimensiones_obstaculo=(1, 1, 1), offset_obstaculos=0, offset_trayectoria=0)
