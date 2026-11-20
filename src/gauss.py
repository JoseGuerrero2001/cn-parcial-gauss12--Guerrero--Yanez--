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
    """ Lleva "a" una forma triangular superior "U" y actualiza "b".
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


        pivote = U[k, k]
        if pivote == 0.0:
            raise ZeroDivisionError(f"Pivote nulo encontrado en el paso {paso_num} (fila {k + 1}).")
        #Eliminacion de filas por debajo de k (solo desde columna k en adelante)
        
        for i in range(k + 1, n):
            # 1 division para calcular el multiplicador de una sola vez por fila
            m_ik = U[i, k] / pivote
            if contador is not None:
                contador.registrar_mult_div(paso_num, 1)
            if abs(m_ik) > max_multiplicador:
                max_multiplicador = abs(m_ik)

            #Anulamos explisitanente la subdiagonal en columna k
            U[i, k] = 0.0

            #Actualizamos columnas j desde k + 1 hasta n - 1
            for j in range(k+1, n):
                #1 multiplicacion (m_ik * U[k, j]) + 1 resta (U[i, j] - prod)
                U[i, j] = U[i, j] - m_ik * U[k, j]
                if contador is not None:
                    contador.registrar_mult_div(paso_num, 1)
                    contador.registrar_suma_resta(paso_num, 1)

            #Actualizamos el lado derecho b[i]
            # una multiplicacion (m_ik * rhs[k]) + 1 resta (rhs[i] - prod)
            rhs[i] = rhs [i] - m_ik * rhs[k]
            if contador is not None:
                contador.registrar_mult_div(paso_num, 1)
                contador.registrar_suma_resta(paso_num, 1)

        max_actual = float(np.max(np.abs(U)))
        if max_actual > max_durante_elim:
            max_durante_elim = max_actual

        traza_lineas.append(f"--- Paso {paso_num}(pivote fila {k + 1}, col {k+1} = {pivote:.6e}) ---")
        traza_lineas.append(formatear_matriz(U))
        traza_lineas.append("")

    factor_crecimiento = max_durante_elim / max_inicial if max_inicial != 0.0 else 0.0

    estadisticas = {

        "pivoteo": pivoteo,
        "max_multiplicador": max_multiplicador,
        "max_inicial": max_inicial,
        "max_durante_elim": max_durante_elim,
        "factor_crecimiento": factor_crecimiento,
        "intercambios_fila": total_intercambios,
    }

    return U, rhs, "\n".join(traza_lineas), estadisticas

def sustitucion_regresiva(
        U: np.ndarray,
        b_mod: np.ndarray,
        contador: contadorflops | None = None,
) -> np.ndarray:
    """Resuelve Ux = b_mod mediante sustitucion regresiva."""
    n = U.shape[0]
    x = np.zeros(n, dtype=np.float64)

    for i in range(n - 1, -1, -1):
        suma = b_mod[i]
        for j in range(i + 1,n):
            # una multiplicacion (U[i, j] * x[j]) +1 resta
            suma = suma - U[i, j] * x[j]
            if contador is not None:
                contador.registrar_mult_div(None, 1)
                contador.registrar_suma_resta(None, 1)

        if U[i,i] == 0.0:
            raise ZeroDivisionError(f"Elemento diagonal nulo en sustitucion regresiva (fila {i+1}).")

        # Una division final para despejar x[i]
        x[i] = suma / U[i,i]
        if contador is not None:
            contador.registrar_mult_div(None, 1)
    return x
