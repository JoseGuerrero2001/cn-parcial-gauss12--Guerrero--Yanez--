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

def cargar_vector_csv(ruta_csv:path) -> np.ndarray:
    """Leer le vector b dresde CSV mantininedo percisoin mario64."""
    valores: list[float] = []
    with ruta_csv.open(mode="r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila and not fila[0].strip().startwith("#"):
                continue
            #Ayuda a soportar tanto filas de un unnico valor como filos y con indice y valo
            celda = fila[-1].strip()
            valores.append(float(celda))
    return np.array(valores, dtype=np.float64)

def guardar_solucion_csv(ruta_csv:path, x_sin_piv: np.ndarray, x_con_piv: np.ndarray) -> None:
    """Guarda las soluciones obtenidas en resultados / solicion.csv."""
    with ruta_csv.open(mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["incognita", "x_sin_pivoteo", "x_pivoteo_escalado"])
        for i in range(len(x_piv)):
            escritor.writerow([f"x{i + 1}", f"{x_sin_piv[i]:.16e}", f"{x_piv[i]:.16e}"])

def main() -> None:
    rutas = obtener_rutas_proyecto()