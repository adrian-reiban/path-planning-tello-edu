from Algoritmos.Algoritmos2D import roadmap, trapezoidacion
from Planning2D.Entornos.EntornosPoligonales.EntornosEjemplo import entorno1
from PlanningPseudo3D.RoadMap.representar_solucion import RepresentarSolucion

# Obteniendo los parámetros del entorno
limites_entorno, obstaculos, start, meta = entorno1.entorno()

# Configurando y ejecutando el algoritmo de Trapezoidación
algoritmo_trapezoidacion = trapezoidacion.Trapezoidacion(limites_entorno, obstaculos)
algoritmo_trapezoidacion.ejecutar()
# Obteniendo los resultados del algoritmo de Trapezoidación
limites_entorno, lineas_divisorias, trapecios, fronteras_trapecios, fronteras_compartidas = \
    algoritmo_trapezoidacion.obtener_resultados()

# Configurando y ejecutando el algoritmo de Roadmap
algoritmo_roadmap = roadmap.RoadMap(trapecios, lineas_divisorias, fronteras_trapecios,
                                    fronteras_compartidas, start, meta)
_, _, _, puntos_trayectoria = algoritmo_roadmap.ejecutar()

# Dibujando el entorno y los resultados
RepresentarSolucion(limites_entorno=limites_entorno, obstaculos=obstaculos, start=start, meta=meta,
                    trayectoria=puntos_trayectoria, altura_obstaculos=120, offset_obstaculos=0, offset_trayectoria=80)
