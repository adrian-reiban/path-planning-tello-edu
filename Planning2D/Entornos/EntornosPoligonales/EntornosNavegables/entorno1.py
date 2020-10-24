# Nota: La coordenada X de cada vertice de los obstáculos que conforman el entorno no debe repetirse;
#       de lo contrario el algoritmo de trapezoidación no funcionará.
#       Otro aspecto importante es que, todos los puntos que correspondan a los obstáculos y los límites del entorno
#       poligonal deben estar especificados en sentido horario.

def entorno():
    # Límites del entorno poligonal
    limites_entorno = [(0, 0), (0, 200), (200, 200), (200, 0)]

    # Obstáculos del entorno
    obstaculo1 = [(40, 110), (30, 130), (60, 160), (80, 120)]
    obstaculo2 = [(120, 85), (140, 170), (160, 110)]
    obstaculo3 = [(50, 25), (60, 60), (90, 60), (85, 30)]
    obstaculos = [obstaculo1, obstaculo2, obstaculo3]

    # Coordenadas Start y Meta
    start = (10, 180)
    meta = (180, 10)

    return [limites_entorno, obstaculos, start, meta]
