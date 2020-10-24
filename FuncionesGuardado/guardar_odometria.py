import pandas as pd
direccion = "../Odometria/"


def guardar_odometria(nombre_archivo, rutas_referenciales, escalas_tiempo, desplazamientos, alturas):
    # Convirtiendo los datos en un diccionario
    datos = {}
    clave_ruta_referencial = "Referencia"   # Trayectoria referencial
    clave_altura = "Altura"
    clave_tiempo = "Tiempo"
    clave_trayectoria = "Trayectoria"

    for iterador1, ruta in enumerate(rutas_referenciales):
        clave = clave_ruta_referencial + str(iterador1 + 1)
        datos[clave] = ruta

    for iterador2, escala in enumerate(escalas_tiempo):
        clave1 = clave_tiempo + str(iterador2 + 1)
        clave2 = clave_trayectoria + str(iterador2 + 1)
        clave3 = clave_altura + str(iterador2 + 1)
        datos[clave1] = escala
        datos[clave2] = desplazamientos[iterador2]
        datos[clave3] = alturas[iterador2]

    # data_frame = pd.DataFrame(data=datos)
    # Se utiliza cuando se trabaja con datos de diferentes tamaños
    df = pd.DataFrame.from_dict(datos, orient="index")
    data_frame = df.transpose()
    # Guardando en formato CSV
    data_frame.to_csv(direccion + nombre_archivo + ".csv")
    # Guardando en formato de Excel
    data_frame.to_excel(direccion + nombre_archivo + ".xlsx")


# Abre el Data Frame en formato CSV y lo devuelve
def abrir_odometria_csv(nombre_archivo):
    datos = pd.read_csv(direccion + nombre_archivo + ".csv", index_col=0)
    return datos


# Abre el Data Frame en formato de Excel y lo devuelve
def abrir_odometria_excel(nombre_archivo):
    datos = pd.read_excel(direccion + nombre_archivo + ".xlsx", index_col=0)
    return datos
