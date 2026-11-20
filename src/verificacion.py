#Extencion de verificacion

import numpy as np
import csv
from decimal import Decimal, getcontext
from pathlib import Path



def estimar_condicionamiento(A: np.ndarray) -> dict[str, float]:
    """
    Estima el numero de condicion kappa_2(A) y la cota clasica de error relativo
    en aritmetica de punto flotante IEEE 754 doble precision.
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
    """Carga la matriz A desde CSV en precision decimal extendida sin truncar."""
    getcontext().prec = precision_digitos
    matriz_dec: list[list[Decimal]] = []
    with ruta_a.open(mode="r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila and not fila[0].strip().startswith("#"):
                matriz_dec.append([Decimal(valor.strip()) for valor in fila])
    return matriz_dec


def cargar_b_decimal(ruta_b: Path, precision_digitos: int = 80) -> list[Decimal]:
    """Carga el vector b desde CSV en precision decimal extendida sin truncar."""
    getcontext().prec = precision_digitos
    vector_dec: list[Decimal] = []
    with ruta_b.open(mode="r", newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if not fila or fila[0].strip().startswith("#"):
                continue
            vector_dec.append(Decimal(fila[-1].strip()))
    return vector_dec


def calcular_residuo_extendido(
    ruta_a: Path,
    ruta_b: Path,
    x: np.ndarray,
    precision_digitos: int = 80,
) -> tuple[list[Decimal], Decimal]:
    """
    Calcula r = b - Ax en precision extendida (Decimal) y retorna (r, ||r||_inf).
    """
    getcontext().prec = precision_digitos
    A_dec = cargar_a_decimal(ruta_a, precision_digitos=precision_digitos)
    b_dec = cargar_b_decimal(ruta_b, precision_digitos=precision_digitos)
    x_dec = [Decimal(repr(float(val))) for val in x]

    n = len(b_dec)
    residuo: list[Decimal] = []
    norma_inf = Decimal("0")

    for i in range(n):
        ax_i = Decimal("0")
        for j in range(n):
            ax_i += A_dec[i][j] * x_dec[j]
        r_i = b_dec[i] - ax_i
        residuo.append(r_i)
        if abs(r_i) > norma_inf:
            norma_inf = abs(r_i)

    return residuo, norma_inf




pass