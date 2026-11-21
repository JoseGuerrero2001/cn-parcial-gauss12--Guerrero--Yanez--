from pathlib import Path
import csv
import numpy as np

from conteo import ContadorFlops
from gauss import eliminacion_gaussiana,sustitucion_regresiva
from verificacion import (
    estimar_condicionamiento,
    calcular_residuo_extendido,
    refinamiento_iterativo,
    control_biblioteca
)





def obtener_rutas_proyecto() -> dict[str, Path]:

    """ Resuelve las rutas base del repositario de forma independiente al directorio actual."""
    raiz = Path(__file__).resolve().parent.parent
    return {
        "raiz": raiz,
        "datos": raiz / "datos",
        "src": raiz / "src",
        "resultados": raiz / "resultados",
    }

def cargar_matriz_csv(ruta_csv: Path) -> np.ndarray:
    """Lee una matriz numérica desde CSV, manteniendo precisión float64."""
    filas: list[list[float]] = []
    with ruta_csv.open(mode="r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila and not fila[0].strip().startswith("#"):
                filas.append([float(valor.strip()) for valor in fila])
    return np.array(filas, dtype=np.float64)


def cargar_vector_csv(ruta_csv: Path) -> np.ndarray:
    """Lee el vector b desde CSV manteniendo precisión float64."""
    valores: list[float] = []
    with ruta_csv.open(mode="r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if not fila or fila[0].strip().startswith("#"):
                continue
            celda = fila[-1].strip()
            valores.append(float(celda))
    return np.array(valores, dtype=np.float64)

def guardar_solucion_csv(ruta_csv:Path, x_sin_piv: np.ndarray, x_con_piv: np.ndarray) -> None:
    """Guarda las soluciones obtenidas en resultados / solicion.csv."""
    with ruta_csv.open(mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["incognita", "x_sin_pivoteo", "x_pivoteo_escalado"])
        for i in range(len(x_con_piv)):
            escritor.writerow([f"x{i + 1}", f"{x_sin_piv[i]:.16e}", f"{x_con_piv[i]:.16e}"])

def main() -> None:
    rutas = obtener_rutas_proyecto()
    carpeta_resultados = rutas["resultados"]
    carpeta_resultados.mkdir(parents=True, exist_ok=True)

    ruta_a = rutas["datos"] / "matriz_a.csv"
    ruta_b = rutas["datos"] / "vector_b.csv"

    a = cargar_matriz_csv(ruta_a)
    b = cargar_vector_csv(ruta_b)

# 1. Corrida sin pivoteo
    contador_sin_piv = ContadorFlops(convencion="1 operacion aritmetica elemental = 1 flop")
    U_sin_piv, b_sin_piv, traza_sin_piv, stats_sin_piv = eliminacion_gaussiana(
        a, b, pivoteo="ninguno", contador=contador_sin_piv
    )
    x_sin_piv = sustitucion_regresiva(U_sin_piv, b_sin_piv, contador=contador_sin_piv)

    #2. Corrida con pivoteo escalado
    contador_piv = ContadorFlops(convencion="1 operacion aritmetica elemental = 1 flop")
    U_piv, b_piv, traza_piv, stats_piv = eliminacion_gaussiana(
        a, b, pivoteo ="parcial_escalado", contador=contador_piv)
    x_piv = sustitucion_regresiva(U_piv, b_piv, contador = contador_piv)

    # 3. Guardar traza de los 11 pasos y reporte de flops
    ruta_traza = carpeta_resultados / "traza_eliminacion.txt"
    with ruta_traza.open(mode="w", encoding ="utf-8") as f_traza:
        f_traza.write("=== TRAZA SIN PIVOTEO ===\n")
        f_traza.write(traza_sin_piv + "\n\n")
        f_traza.write("=== TRAZA CON PIVOTEO PARCIAL ESCALADO ===\n")
        f_traza.write(traza_piv + "\n")

    ruta_flops = carpeta_resultados / "conteo_flops.md"
    contenido_flops = (
        "# Conteo de Operaciones (FLOPs)\n\n"
        + contador_sin_piv.generar_reporte_markdown("Sin mivoteo")
        +"\n---\n\n"
        + contador_piv.generar_reporte_markdown("Con Pivoteo pracial Escalado")
    )
    ruta_flops.write_text(contenido_flops, encoding="utf-8")

    # 4.Veridicion en percision extendida, cindonamiento y refinamiento
    info_cond = estimar_condicionamiento(a)
    residuo_inicial, norma_inf_inicial = calcular_residuo_extendido(ruta_a, ruta_b, x_piv)
    x_refinado, norma_inf_refinado, iter_ref = refinamiento_iterativo(
        ruta_a, ruta_b, x_piv, eliminacion_gaussiana, sustitucion_regresiva
    )
    x_ref = control_biblioteca(a, b)

    guardar_solucion_csv(carpeta_resultados / "solucion.csv", x_sin_piv, x_refinado)
    ruta_residuo = carpeta_resultados / "residuo.txt"
    lineas_residuo = [
        f"condicionamiento kappa_2(a): {info_cond['kappa_2']:.6e}",
        f"cota kappa(a) * eps: {info_cond['cota_error_relativo']:.6e}",
        f"norma infinito residuo inicial ||b - Ax||_inf: {norma_inf_inicial}",
        f"iteraciones de refinamiento iterativo: {iter_ref}",
        f"norma infinito residuo tras refinado: {norma_inf_refinado}",
        "vector residuo inicial r = b - Ax:",
    ]    
    for idx, val in enumerate(residuo_inicial, start=1):
        lineas_residuo.append(f" r[{idx}] = {val}")
    lineas_residuo.append("\nConparacion normal L2 fentre a numpy.linalg.solve:")
    lineas_residuo.append(f" ||x_piv - x_ref||_2 = {np.linalg.norm(x_piv - x_ref):.6e}")
    lineas_residuo.append(f" ||x_refinado - x_ref||_2 = {np.linalg.norm(x_refinado - x_ref):.6e}")

    ruta_residuo.write_text("\n".join(lineas_residuo) + "\n", encoding="utf-8")

    print("Ejecucion completada. Archivos generados en 'resutados/'.")
    """
    print("--- Estadísticas Sin Pivoteo ---")
    print(f"max_multiplicador: {stats_sin_piv['max_multiplicador']:.6e}")
    print(f"factor_crecimiento: {stats_sin_piv['factor_crecimiento']:.6e}")

    print("--- Estadísticas Pivoteo Parcial Escalado ---")
    print(f"max_multiplicador: {stats_piv['max_multiplicador']:.6e}")
    print(f"factor_crecimiento: {stats_piv['factor_crecimiento']:.6e}")
    """

if __name__ == "__main__":
    main()

