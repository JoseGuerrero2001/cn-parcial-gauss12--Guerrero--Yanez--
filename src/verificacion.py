#Extencion de verificacion

import numpy as np

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

