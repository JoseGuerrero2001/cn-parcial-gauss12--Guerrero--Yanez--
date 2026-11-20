from pathlib import path
import csv
import numpy as np

from conteo import contadorflops
from gauss import eliminacion_gaussiana,sustitucion_regresiva
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
    carpeta_resultados = rutas["resultados"]
    carpeta_resultados.mkdir(parents=True, exist_ok=True)

    ruta_a = rutas["datos"] / "matriz_a.csv"
    ruta_b = rutas["datos"] / "vector_b.csv"

    a = cargar_matriz_csv(ruta_a) 
    b = cargar_vector_csv(ruta_b)

    # 1. Corrida sin pivoteo
    contador_sin_piv = ContadorFlops(convencion="1 operacion aritmetica elemental = 1 flop")
    U_sin_piv, b_sin_piv = traz_sin_piv, stats_sin_piv = eliminacion_gaussiana(
        a, b, pivoteo ="ninguno", contador=contador_sin_piv
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

def formatear_matriz(M: np.ndarray, decimales: int = 4) -> str:
    """Formatea una matriz de forma legible para la traza de pasos."""
    lineas = []
    for fila in M:
        elementos = " ".join(f"{val:{decimales + 7}.{decimales}e}" for val in fila)
        lineas.append(f"[{elementos}]")
    return "\n".join(lineas)

def eliminacion_gaussiana(
        a: np.ndarray,
        b: np.ndarray,
        pivoteo: str = "ninguno",
        contador: Contadorflops | None = None
) -> tuple[np.ndarray, np.ndarray, str, dict]:
    """ Lleva A a una forma triangular superior U y actualiza b.
    pivoteo: "ninguno" o "parcial escalado"."
    retorna: (U, b_modificado, traza, estadisticas)
    """
    U = np.array(a, dtype=np.float64, copy=True)
    rhs = np.array(b, dtype=np.float64, copy=True)
    n = U.shape[0]

    max_inicial = float(np.max(np.abs(U)))
    max_durante_elim = max_inicial
    max_multiplicador = 0.0
    total_intercambios = 0

    # Factores de escala por fila (maximo absoluto de cada fila al inicio)
    #Se usan unicamente si pivoteo == "parcial_escalado"
    escalas = np.max(np.abs(U), axis=1)
    
    traza_lineas: list[str]= [
        f"matriz inicial A (max |a_ij| = {max_inicial:.6e}):",
        formatear_matriz(U),
        "",
    ]

    for k in range(n-1):
        paso_num = k + 1 #Pasos 1 a 11 para realizar n=12

        if pivoteo == "parcial escalado":
            fila_pivote = k
            mejor_razon = -1.0
            for i in range(k,n):
                if contador is not None:
                    contador.registrar_comparacion_pivote(paso_num, 1)
                escala_i = escalas[i] if escalas [i] != 0.0 else 1.0
                razon = abs(U[i,k]) / escala_i
                if razon > mejor_razon:
                    mejor_razon = razon
                    fila_pivote = i

            if fila_pivote != k:
                U[[k, fila_pivote], :] = U[[fila_pivote, k], :]
                rhs[[k, fila_pivote]] = rhs [[fila_pivote, k]]
                escalas[[k, fila_pivote]] = escalas[[fila_pivote, k]]
                total_intercambios +=1
                if contador is not None:
                    contador.registrar_intercambio_fila(paso_num, 1)




if __name__ == "__main__":
    main()
    