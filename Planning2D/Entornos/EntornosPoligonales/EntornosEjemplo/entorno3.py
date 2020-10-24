# Nota: La coordenada X de cada vertice de los obstáculos que conforman el entorno no debe repetirse;
#       de lo contrario el algoritmo de trapezoidación no funcionará.
#       Otro aspecto importante es que, todos los puntos que correspondan a los obstáculos y los límites del entorno
#       poligonal deben estar especificados en sentido horario.

def entorno():
    # Límites del entorno poligonal
    limites_entorno = [(0, 0), (0, 100), (100, 100), (100, 0)]

    # Obstáculos del entorno
    obstaculo1 = [(10, 30), (20, 60), (15, 75), (30, 65)]
    obstaculo2 = [(40, 10), (45, 90), (90, 90), (85, 85), (50, 85), (47, 30), (70, 30), (65, 45), (55, 45),
                  (60, 55), (80, 55), (95, 10)]
    obstaculo3 = [(62, 60), (74, 80), (78, 60)]
    obstaculos = [obstaculo1, obstaculo2, obstaculo3]

    # Coordenadas Start y Meta
    start = (5, 10)
    meta = (62.5, 37)

    return [limites_entorno, obstaculos, start, meta]
