from pathlib import path
import csv
import numpy as np

from conteo import contadorflops
from gauss import eliminacion_gaussiana,
sustitucion_regresiva
from verificacion import (
    estimar_condicionamiento,
    calcular_residuo_extendido,
    refinamiento_iterativo,
    control_biblioteca
)
def obtener_rutas_proyecto() dict[str, path]:

    """ Resuelve las rutas base del repositario de forma independiente al directorio actual."""
    raiz = path(__file__).resolve().parent.parent
    return {
        "raiz": raiz,
        "datos": raiz / "datos",
        "src": raiz / "src",
        "resultados": raiz / "resultados",
    }

def cargar_matriz_csv(ruta_csv:path) -> np.ndarray:
    """ Leer una matriz numerica dresde CSV, manteniendo precision float64."""
    filas: list[list[float]] = []
    with ruta_csv.open(mode="r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila and not fila[0].strip().startwith("#"):
                filas.append([float(valor) for valor in fila])
                return np.array(filas, dtype=np.float64)
    