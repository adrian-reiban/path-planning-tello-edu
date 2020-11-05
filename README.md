# Sistema-Planificacion-Tello-EDU
Sistema de planificación de rutas y ejecución de trayectorias para el Tello EDU

Las secciones que se listan a continuación pueden usarse por separado para pruebas experimentales y de ampliación del código:
* Planning2D: Contiene ejemplos animados acerca del funcionamiento de los algoritmos de Grassfire, Dijkstra, A* en entornos discretos; así como la discretización trapezoidal de un entorno poligonal.
* PlanningPseudo3D: Presenta la solución tridimensional del camino formado por un proceso de búsqueda bidimensional.
* Planning3D: Programa para la construcción de mundos voxelizados y la ejecución de algoritmos de búsqueda.

El control de los Tello EDU se realiza a través del programa main.py, dentro de la carpeta ControlDrone. Los Tello EDU deben estar previamente configurados en modo AP utilizando el programa alojado en la carpeta ModoAP

Requisitos para el funcionamiento de los programas:
* Python 3.8
* Numpy 1.19.1
* Matplotlib 3.3.2
* Pandas 1.1.3
* Shapely >=1.7.1
* PyQt 5.12.3
* PyOpenGL 3.1.5
* PyQtGraph 0.11.0
* vtk 9.0.1
* Vedo Python 2020.4.0
* Panda3D >=1.10.6

Para facilitar la instalación de los requisitos previos, usar Anaconda Individual Edition y en la ventana de comandos ejecutar lo siguiente:
### conda install -c conda-forge shapely (Shapely: https://shapely.readthedocs.io/en/stable/manual.html)
### conda install -c conda-forge pyqtgraph (PyQtGraph: http://www.pyqtgraph.org/)
### pip install PyOpenGL PyOpenGL_accelerate (PyOpenGL: http://pyopengl.sourceforge.net/)
### conda install -c conda-forge vedo (Vedo Python: https://github.com/marcomusy/vedo)
### pip install panda3d==1.10.7 (Panda3D: https://www.panda3d.org/)

Ejecutados los comandos de instalación anteriores, Anaconda instalará los componentes faltantes...
