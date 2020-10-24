# Nota: La coordenada X de cada vertice de los obstáculos que conforman el entorno no debe repetirse;
#       de lo contrario el algoritmo de trapezoidación no funcionará.
#       Otro aspecto importante es que, todos los puntos que correspondan a los obstáculos y los límites del entorno
#       poligonal deben estar especificados en sentido horario.

def entorno():
    # Límites del entorno poligonal
    limites_entorno = [(0, 0), (0, 400), (400, 400), (400, 0)]

    # Obstáculos del entorno
    """obstaculo1 = [(5, 75), (15, 90), (12, 75)]
    obstaculo2 = [(10, 10), (30, 30), (20, 50), (40, 40), (60, 50), (50, 30), (70, 10), (45, 0)]
    obstaculo3 = [(75, 50), (77, 80), (95, 30)]
    obstaculo4 = [(25, 70), (27, 91), (35, 85), (33, 75)]
    obstaculo5 = [(81, 18), (85, 33), (90, 20)]
    obstaculo6 = [(23, 39), (27, 32), (21, 30)]
    obstaculo7 = [(52, 30), (55, 32), (57, 25)]"""
    obstaculo1 = [(20, 300), (60, 360), (48, 300)]
    obstaculo2 = [(40, 40), (120, 120), (80, 200), (160, 160), (240, 200), (200, 120), (280, 40), (128, 0)]
    obstaculo3 = [(300, 200), (308, 320), (380, 120)]
    obstaculo4 = [(100, 280), (108, 364), (140, 340), (132, 300)]
    obstaculo5 = [(324, 72), (340, 132), (360, 80)]
    obstaculo6 = [(92, 156), (108, 128), (84, 120)]
    obstaculo7 = [(208, 120), (220, 128), (228, 100)]
    obstaculos = [obstaculo1, obstaculo2, obstaculo3, obstaculo4, obstaculo5, obstaculo6, obstaculo7]

    # Coordenadas Start y Meta
    start = (10, 10)
    meta = (360, 244)

    return [limites_entorno, obstaculos, start, meta]
