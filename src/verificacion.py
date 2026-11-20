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
    with ruta_a.open(mode="r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila and not fila[0].strip().startswith("#"):
                matriz_dec.append([Decimal(valor.strip()) for valor in fila])
    return matriz_dec


def cargar_b_decimal(ruta_b: Path, precision_digitos: int = 80) -> list[Decimal]:
    """Carga el vector b desde CSV en precision decimal extendida sin truncar."""
    getcontext().prec = precision_digitos
    vector_dec: list[Decimal] = []
    with ruta_b.open(mode="r", newline="", encoding="utf-8-sig") as archivo:
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



def refinamiento_iterativo(
    ruta_a: Path,
    ruta_b: Path,
    x_inicial: np.ndarray,
    fn_eliminacion,
    fn_sustitucion,
    max_pasadas: int = 3,
    precision_digitos: int = 80,
    ) -> tuple[np.ndarray, Decimal, int]:
    """
    Aplica refinamiento iterativo usando el residuo r = b - Ax calculado en
    precision extendida y resolviendo A * delta_x = r en float64.
    Retorna: (x_mejorado, norma_inf_final, pasadas_ejecutadas)
    """
    getcontext().prec = precision_digitos
    A_fp64 = cargar_a_decimal(ruta_a, precision_digitos=precision_digitos)
    A_num = np.array([[float(val) for val in fila] for fila in A_fp64], dtype=np.float64)

    x_actual = np.array(x_inicial, dtype=np.float64, copy=True)
    _, norma_inf_actual = calcular_residuo_extendido(
        ruta_a, ruta_b, x_actual, precision_digitos=precision_digitos
    )

    pasadas = 0
    for _ in range(max_pasadas):
        residuo_dec, _ = calcular_residuo_extendido(
            ruta_a, ruta_b, x_actual, precision_digitos=precision_digitos
        )
        r_num = np.array([float(val) for val in residuo_dec], dtype=np.float64)

        U_aux, r_mod, _, _ = fn_eliminacion(A_num, r_num, pivoteo="parcial_escalado", contador=None)
        delta_x = fn_sustitucion(U_aux, r_mod, contador=None)

        x_candidato = x_actual + delta_x
        _, norma_inf_candidato = calcular_residuo_extendido(
            ruta_a, ruta_b, x_candidato, precision_digitos=precision_digitos
        )

        pasadas += 1
        # Solo aceptamos la corrección si reduce la norma infinito del residuo
        if norma_inf_candidato < norma_inf_actual:
            x_actual = x_candidato
            norma_inf_actual = norma_inf_candidato
        else:
            break

    return x_actual, norma_inf_actual, pasadas


def control_biblioteca(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solucion de referencia de control usando numpy.linalg.solve."""
    return np.linalg.solve(np.array(A, dtype=np.float64), np.array(b, dtype=np.float64))


pass