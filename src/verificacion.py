#Extencion de verificacion

import numpy as np
import csv
from decimal import Decimal, getcontext
from pathlib import Path



def estimar_condicionamiento(A: np.ndarray) -> dict[str, float]:
    """
    Estima el número de condición kappa_2(A) y la cota clásica de error relativo
    en aritmética de punto flotante IEEE 754 doble precisión.
    """
    A_fp64 = np.array(A, dtype=np.float64)
    kappa_2 = float(np.linalg.cond(A_fp64, p=2))
    eps_maquina = float(np.finfo(np.float64).eps)  # ~2.220446049250313e-16
    cota_error_relativo = kappa_2 * eps_maquina

    return {
        "kappa_2": kappa_2,
        "eps_maquina": eps_maquina,
        "cota_error_relativo": cota_error_relativo,
    }

def cargar_a_decimal(ruta_a: Path, precision_digitos: int = 80) -> list[list[Decimal]]:
    """Carga la matriz A desde CSV en precisión decimal extendida sin truncar."""
    getcontext().prec = precision_digitos
    matriz_dec: list[list[Decimal]] = []
    with ruta_a.open(mode="r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila and not fila[0].strip().startswith("#"):
                matriz_dec.append([Decimal(valor.strip()) for valor in fila])
    return matriz_dec

def cargar_b_decimal(ruta_b: Path, precision_digitos: int = 80) -> list[Decimal]:
    """Carga el vector b desde CSV en precisión decimal extendida sin truncar."""
    getcontext().prec = precision_digitos
    vector_dec: list[Decimal] = []
    with ruta_b.open(mode="r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if not fila or fila[0].strip().startswith("#"):
                continue
            vector_dec.append(Decimal(fila[-1].strip()))
    return vector_dec


pass