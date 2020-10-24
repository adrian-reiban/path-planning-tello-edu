# Nota: La coordenada X de cada vertice de los obstáculos que conforman el entorno no debe repetirse;
#       de lo contrario el algoritmo de trapezoidación no funcionará.
#       Otro aspecto importante es que, todos los puntos que correspondan a los obstáculos y los límites del entorno
#       poligonal deben estar especificados en sentido horario.

def entorno():
    # Límites del entorno poligonal
    limites_entorno = [(0, 0), (0, 100), (100, 100), (100, 0)]

    # Obstáculos del entorno
    obstaculo1 = [(5, 60), (12.5, 90), (30, 75)]
    obstaculo2 = [(40, 30), (50, 60), (90, 60), (80, 30)]
    obstaculos = [obstaculo1, obstaculo2]

    # Coordenadas Start y Meta
    start = (10, 50)
    meta = (95, 15)

    return [limites_entorno, obstaculos, start, meta]
