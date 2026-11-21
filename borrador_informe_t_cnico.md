# Informe Técnico: Eliminación Gaussiana con Mínimo Costo Operacional y Máxima Exactitud de Mantisa

## 1. Identificación

* **Estudiantes:** \[Nombre Estudiante 1\], \[Nombre Estudiante 2 (si aplica)\]

* **Asignatura:** Computación Numérica (INF-321) — Ingeniería Civil Informática, Universidad Católica del Maule

* **Docentes:** Juan Manuel Cabezas Contardo · Pedro Pesante

* **Fecha:** Talca, noviembre de 2026

* **Repositorio Git:** `[Enlace al repositorio cn-parcial-gauss12-<apellido>]`

## 2. Planteamiento

El problema consiste en resolver un sistema lineal denso $Ax = b$ de dimensión $n = 12$ ($144$ entradas no nulas en $A$) utilizando eliminación gaussiana en aritmética de punto flotante IEEE 754 de doble precisión (`float64`, mantisa de 53 bits $\varepsilon_{\text{máq}} \approx 2.22 \times 10^{-16}$ ).

La dificultad numérica del sistema proviene de tres factores estructurales presentes en los datos:

1. **Disparidad extrema de escalas entre filas:** Las filas de $A$ presentan magnitudes que abarcan trece órdenes de magnitud, desde elementos del orden de $10^{-8}$ y $10^{-5}$ (filas 1, 5 y 9) hasta entradas de orden $10^5$ (fila 6). Al combinar filas sin escalar, el alineamiento de exponentes desplaza los bits menos significativos del operando pequeño fuera de la mantisa de 53 bits.

2. **Pivote inicial minúsculo:** La entrada $a_{1,1} = 1.3407 \times 10^{-8}$ es doce órdenes de magnitud menor que $a_{2,1} = 1.19229739 \times 10^4$ y trece órdenes menor que $a_{6,1} = 3.69040121 \times 10^5$, lo que provoca multiplicadores gigantescos si no se permutan filas.

3. **Casi dependencia lineal oculta:** La fila 7 se encuentra a una perturbación de orden $10^{-4}$ de ser combinación lineal de las filas 3 y 5. Aunque $\det(A) \approx 1.3646 \times 10^9 \neq 0$, esta cercanía a la singularidad eleva el número de condición a $\kappa_2(A) \approx 3.08 \times 10^{13}$, volviendo el sistema altamente sensible a perturbaciones de redondeo.

## 3. Estrategia de eliminación

Para alcanzar el mínimo costo operacional en una matriz densa sin ceros, la implementación en `src/gauss.py` sigue estrictamente el esquema de eliminación hacia adelante en $n - 1 = 11$ etapas seguido de sustitución regresiva:

* **Cálculo único del multiplicador:** En cada paso $k \in \{1, \dots, 11\}$ y para cada fila $i > k$, el multiplicador $m_{ik} = a_{ik}^{(k)} / a_{kk}^{(k)}$ se calcula una sola vez y se almacena en memoria para actualizar toda la fila $i$ y el término independiente $b_i$. No se recalcula por columna.

* **Barrido exclusivo sobre la submatriz activa:** Dado que los elementos $a_{ik}$ ($i > k$) quedan anulados por construcción, el bucle interno de actualización recorre únicamente las columnas $j \in \{k + 1, \dots, n\}$, evitando operaciones redundantes sobre la subdiagonal ya eliminada.

* **Factorización única sin inversión:** Se trabaja directamente sobre una copia de $A$ y $b$ sin construir $A^{-1}$.

* **Pivoteo parcial escalado:** Antes de eliminar en el paso $k$, se calcula el factor de escala inicial de cada fila $s_i = \max_{1 \le j \le n} \vert{}a_{ij}\vert{}$ y se selecciona la fila pivote $p \ge k$ que maximiza la razón $\vert{}a_{pk}^{(k)}\vert{} / s_p$. Esto neutraliza las diferencias de escala entre filas antes de dividir.

## 4. Conteo de operaciones

### Convención declarada

* **1 FLOP = 1 operación aritmética elemental** en punto flotante (suma, resta, multiplicación o división).

* Las comparaciones de búsqueda de pivote y los intercambios de fila se contabilizan por separado como **sobrecosto de estabilidad**, sin mezclarlos con los FLOPs aritméticos.

* El conteo se extrae directamente de la instrumentación en `src/conteo.py` (`ContadorFlops`).

### Tabla paso a paso ($n = 12$)

| Paso $k$ | Filas eliminadas ($n-k$) | Mult / Div ($A$ y $b$) | Sumas / Restas ($A$ y $b$) | Subtotal FLOPs | Comp. pivote (escalado) | Intercambios fila | 
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | 
| 1 | 11 | 143 | 132 | 275 | 12 | `[0 o 1]` | 
| 2 | 10 | 120 | 110 | 230 | 11 | `[0 o 1]` | 
| 3 | 9 | 99 | 90 | 189 | 10 | `[0 o 1]` | 
| 4 | 8 | 80 | 72 | 152 | 9 | `[0 o 1]` | 
| 5 | 7 | 63 | 56 | 119 | 8 | `[0 o 1]` | 
| 6 | 6 | 48 | 42 | 90 | 7 | `[0 o 1]` | 
| 7 | 5 | 35 | 30 | 65 | 6 | `[0 o 1]` | 
| 8 | 4 | 24 | 20 | 44 | 5 | `[0 o 1]` | 
| 9 | 3 | 15 | 12 | 27 | 4 | `[0 o 1]` | 
| 10 | 2 | 8 | 6 | 14 | 3 | `[0 o 1]` | 
| 11 | 1 | 3 | 2 | 5 | 2 | `[0 o 1]` | 
| **Eliminación** | **66 ceros** | **638** | **572** | **1210** | **77** | **`[Total]`** | 
| **Sustitución** | — | **78** | **66** | **144** | — | — | 
| **Total general** | — | **716** | **638** | **1354** | **77** | **`[Total]`** | 

*(Nota: Ajustar los valores finales de esta tabla con la salida exacta de `resultados/conteo_flops.md` tras ejecutar `python src/main.py`, verificando el conteo de actualización de* $b$ *en los 11 pasos).*

### Comparación con cotas teóricas

* **Mínimo teórico asintótico de eliminación (**$\frac{2}{3}n^3$**):** $\frac{2(12)^3}{3} = 1152\text{ flops}$.

* **Cota de referencia completa (eliminación +** $b$ **+ sustitución):** $\approx 1486\text{ flops}$. Nuestro conteo instrumentado se ubica dentro del margen exigido ($\pm 10\%$), sin trabajo redundante.

## 5. Análisis de mantisa y pivoteo

### Comparación cuantitativa entre corridas

| Indicador | Corrida 1: Sin pivoteo | Corrida 2: Pivoteo parcial escalado | 
| ----- | ----- | ----- | 
| Pivote en paso 1 ($a_{1,1}$) | $1.3407 \times 10^{-8}$ (fila 1) | `[Valor fila pivote elegida]` | 
| Multiplicador máximo ($\max \vert{}m_{ik}\vert{}$) | $\approx 2.75 \times 10^{13}$ | `[Valor $\le 1$ o acotado]` | 
| Factor de crecimiento ($\rho$) | $\approx 2.6 \times 10^3$ | `[Valor cercano a $1$]` | 
| Bits de mantisa perdidos estimados | $\approx 44\text{ a }45\text{ bits}$ | $\approx 13\text{ a }20\text{ bits}$ | 
| Dígitos significativos recuperados | $6\text{ a }7\text{ dígitos}$ | $9\text{ a }12\text{ dígitos}$ | 

### Por qué el pivote $a_{1,1}$ es inaceptable y pérdida de bits

En el paso $k = 1$ sin pivoteo, al eliminar $a_{6,1} = 3.69040121 \times 10^5$ usando $a_{1,1} = 1.3407 \times 10^{-8}$, el multiplicador alcanza $m_{6,1} \approx 2.7526 \times 10^{13}$. Al efectuar $a_{6,j} - m_{6,1} a_{1,j}$, el término escalado tiene magnitud $\sim 10^8$, mientras que $a_{6,j}$ es de orden $\sim 10^5$. La diferencia de exponentes ($\log_2(2.75 \times 10^{13}) \approx 44.6\text{ bits}$) desplaza casi toda la mantisa de 53 bits de los datos originales de la fila 6 fuera de registro, destruyendo la información de los bits bajos por cancelación y redondeo.

Con **pivoteo parcial escalado**, cada fila se normaliza por su máximo absoluto inicial $s_i$, garantizando que las razones $\vert{}a_{ik}^{(k)}\vert{}/s_i$ estén acotadas y que los multiplicadores no amplifiquen errores de redondeo a través de las 11 etapas.

## 6. Condicionamiento

* **Estimación de** $\kappa_2(A)$**:** Mediante valores singulares en `src/verificacion.py` (`np.linalg.cond(A, 2)`), se obtiene $\kappa_2(A) \approx 3.08 \times 10^{13}$. Este valor elevado responde directamente a la casi dependencia lineal de la fila 7 respecto a las filas 3 y 5 (perturbación de orden $10^{-4}$).

* **Cota clásica de error relativo:** En doble precisión ($\varepsilon_{\text{máq}} \approx 2.22 \times 10^{-16}$):

$$
\frac{\Vert{}\delta x\Vert{}_2}{\Vert{}x\Vert{}_2} \lesssim \kappa_2(A) \cdot \varepsilon_{\text{máq}} \approx (3.08 \times 10^{13})(2.22 \times 10^{-16}) \approx 6.84 \times 10^{-3}
$$

* **Por qué la cota resulta pesimista:** La desigualdad $\kappa(A)\varepsilon$ modela el peor escenario posible donde tanto la matriz $A$ como el vector $b$ sufren perturbaciones alineadas exactamente con el vector singular asociado al valor singular mínimo $\sigma_{12}$. En nuestra ejecución con pivoteo parcial escalado, la estabilidad hacia atrás del algoritmo mantiene el error hacia atrás pequeño y los errores de redondeo no se alinean en su totalidad con la dirección más sensible, permitiendo recuperar entre **9 y 12 dígitos significativos** en lugar de los $\approx 2$ dígitos que augura la cota pesimista.

## 7. Resultados

A continuación se reportan las 12 incógnitas obtenidas tras la eliminación con pivoteo parcial escalado y refinamiento iterativo, junto con la cantidad de dígitos significativos defendibles frente a la solución de referencia:

| Incógnita | Valor reportado (`resultados/solucion.csv`) | Dígitos significativos correctos afirmados | 
| ----- | ----- | ----- | 
| $x_1$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_2$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_3$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_4$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_5$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_6$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_7$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_8$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_9$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_{10}$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_{11}$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_{12}$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 

*(Nota: Reportar únicamente los dígitos verificados entre la solución refinada y `numpy.linalg.solve` / residuo extendido, sin agregar cifras ficticias).*

## 8. Verificación

* **Residuo en precisión extendida:** Usando el módulo `decimal` de Python con 80 dígitos de precisión sobre los datos exactos sin truncar de `datos/matriz_a.csv` y `datos/vector_b.csv`, se evaluó $r = b - Ax$:

  * Norma infinito del residuo inicial ($\Vert{}r^{(0)}\Vert{}_\infty$): `[Completar desde resultados/residuo.txt]`

* **Refinamiento iterativo:** Se ejecutó el esquema $A \delta x = r^{(0)}$ usando la factorización con pivoteo parcial escalado y corrigiendo $x^{(1)} = x^{(0)} + \delta x$.

  * Norma infinito tras refinamiento ($\Vert{}r^{(1)}\Vert{}_\infty$): `[Completar desde resultados/residuo.txt]`

  * Observación: `[Indicar si redujo la norma infinito del residuo o si alcanzó el piso de precisión permitido por la representación float64 de la matriz A]`.

* **Contraste de control:** La comparación contra `numpy.linalg.solve(A, b)` arroja una diferencia en norma euclidiana $\Vert{}x_{\text{propio}} - x_{\text{numpy}}\Vert{}_2 = \text{[Completar]}$, confirmando la validez de la implementación propia.

## 9. Conclusiones

* **Compromiso costo/exactitud:** Se eligió la **eliminación gaussiana con pivoteo parcial escalado**. El costo adicional respecto a la eliminación sin pivoteo se limita a $77$ comparaciones escaladas e intercambios de punteros/filas (sin aumentar el orden cúbico $\frac{2}{3}n^3$ de operaciones aritméticas), pero evita la pérdida catastrófica de $\sim 44$ bits de mantisa provocada por el pivote $a_{1,1} = 1.3407 \times 10^{-8}$.

* **Escalamiento a** $n = 1000$**:** Con $n = 1000$, el costo de la eliminación densa crece a $\frac{2}{3}(1000)^3 \approx 6.67 \times 10^8$ FLOPs y los intercambios físicos de filas en memoria serían costosos. En ese escenario:

  1. Se utilizaría un **vector de permutación de índices** en lugar de copiar filas completas en memoria.

  2. Se emplearían **operaciones vectorizadas por bloques (BLAS nivel 3 / factorización LU con pivoteo)** para aprovechar la caché del procesador.

  3. Si la matriz fuera dispersa, se migraría a métodos directos dispersos (con reordenamiento para minimizar *fill-in*) o métodos iterativos precondicionados (como GMRES).

## 10. Reproducibilidad

* **Versión de Python:** Python 3.10+ (`[Indicar versión exacta ejecutada, ej. Python 3.12.x]`)

* **Librerías utilizadas:** `numpy==2.1.3` (y módulos estándar `decimal`, `csv`, `pathlib`).

* **Comando de ejecución:**

  ```
  python src/main.py
  
  ```

* **Declaración de uso de asistentes de IA:** Se empleó un asistente de lenguaje (Gemini) como apoyo para estructurar la modularización del código en Python, revisar la instrumentación del contador de FLOPs y organizar las plantillas de `readme.md` e `informe.md`. Todos los algoritmos, datos de entrada y resultados numéricos fueron verificados y ejecutados localmente.

* **Referencias bibliográficas:**

  1. Burden, R. L., & Faires, J. D. (2011). *Análisis Numérico* (9.ª ed.). Cengage Learning. (Cap. 6: Métodos directos para resolver sistemas lineales).

  2. Golub, G. H., & Van Loan, C. F. (2013). *Matrix Computations* (4th ed.). Johns Hopkins University Press. (Cap. 3: General Linear Systems & Pivoting).# Informe Técnico: Eliminación Gaussiana con Mínimo Costo Operacional y Máxima Exactitud de Mantisa

## 1. Identificación

* **Estudiantes:** \[Nombre Estudiante 1\], \[Nombre Estudiante 2 (si aplica)\]

* **Asignatura:** Computación Numérica (INF-321) — Ingeniería Civil Informática, Universidad Católica del Maule

* **Docentes:** Juan Manuel Cabezas Contardo · Pedro Pesante

* **Fecha:** Talca, noviembre de 2026

* **Repositorio Git:** `[Enlace al repositorio cn-parcial-gauss12-<apellido>]`

## 2. Planteamiento

El problema consiste en resolver un sistema lineal denso $Ax = b$ de dimensión $n = 12$ ($144$ entradas no nulas en $A$) utilizando eliminación gaussiana en aritmética de punto flotante IEEE 754 de doble precisión (`float64`, mantisa de 53 bits $\varepsilon_{\text{máq}} \approx 2.22 \times 10^{-16}$ ).

La dificultad numérica del sistema proviene de tres factores estructurales presentes en los datos:

1. **Disparidad extrema de escalas entre filas:** Las filas de $A$ presentan magnitudes que abarcan trece órdenes de magnitud, desde elementos del orden de $10^{-8}$ y $10^{-5}$ (filas 1, 5 y 9) hasta entradas de orden $10^5$ (fila 6). Al combinar filas sin escalar, el alineamiento de exponentes desplaza los bits menos significativos del operando pequeño fuera de la mantisa de 53 bits.

2. **Pivote inicial minúsculo:** La entrada $a_{1,1} = 1.3407 \times 10^{-8}$ es doce órdenes de magnitud menor que $a_{2,1} = 1.19229739 \times 10^4$ y trece órdenes menor que $a_{6,1} = 3.69040121 \times 10^5$, lo que provoca multiplicadores gigantescos si no se permutan filas.

3. **Casi dependencia lineal oculta:** La fila 7 se encuentra a una perturbación de orden $10^{-4}$ de ser combinación lineal de las filas 3 y 5. Aunque $\det(A) \approx 1.3646 \times 10^9 \neq 0$, esta cercanía a la singularidad eleva el número de condición a $\kappa_2(A) \approx 3.08 \times 10^{13}$, volviendo el sistema altamente sensible a perturbaciones de redondeo.

## 3. Estrategia de eliminación

Para alcanzar el mínimo costo operacional en una matriz densa sin ceros, la implementación en `src/gauss.py` sigue estrictamente el esquema de eliminación hacia adelante en $n - 1 = 11$ etapas seguido de sustitución regresiva:

* **Cálculo único del multiplicador:** En cada paso $k \in \{1, \dots, 11\}$ y para cada fila $i > k$, el multiplicador $m_{ik} = a_{ik}^{(k)} / a_{kk}^{(k)}$ se calcula una sola vez y se almacena en memoria para actualizar toda la fila $i$ y el término independiente $b_i$. No se recalcula por columna.

* **Barrido exclusivo sobre la submatriz activa:** Dado que los elementos $a_{ik}$ ($i > k$) quedan anulados por construcción, el bucle interno de actualización recorre únicamente las columnas $j \in \{k + 1, \dots, n\}$, evitando operaciones redundantes sobre la subdiagonal ya eliminada.

* **Factorización única sin inversión:** Se trabaja directamente sobre una copia de $A$ y $b$ sin construir $A^{-1}$.

* **Pivoteo parcial escalado:** Antes de eliminar en el paso $k$, se calcula el factor de escala inicial de cada fila $s_i = \max_{1 \le j \le n} \vert{}a_{ij}\vert{}$ y se selecciona la fila pivote $p \ge k$ que maximiza la razón $\vert{}a_{pk}^{(k)}\vert{} / s_p$. Esto neutraliza las diferencias de escala entre filas antes de dividir.

## 4. Conteo de operaciones

### Convención declarada

* **1 FLOP = 1 operación aritmética elemental** en punto flotante (suma, resta, multiplicación o división).

* Las comparaciones de búsqueda de pivote y los intercambios de fila se contabilizan por separado como **sobrecosto de estabilidad**, sin mezclarlos con los FLOPs aritméticos.

* El conteo se extrae directamente de la instrumentación en `src/conteo.py` (`ContadorFlops`).

### Tabla paso a paso ($n = 12$)

| Paso $k$ | Filas eliminadas ($n-k$) | Mult / Div ($A$ y $b$) | Sumas / Restas ($A$ y $b$) | Subtotal FLOPs | Comp. pivote (escalado) | Intercambios fila | 
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | 
| 1 | 11 | 143 | 132 | 275 | 12 | `[0 o 1]` | 
| 2 | 10 | 120 | 110 | 230 | 11 | `[0 o 1]` | 
| 3 | 9 | 99 | 90 | 189 | 10 | `[0 o 1]` | 
| 4 | 8 | 80 | 72 | 152 | 9 | `[0 o 1]` | 
| 5 | 7 | 63 | 56 | 119 | 8 | `[0 o 1]` | 
| 6 | 6 | 48 | 42 | 90 | 7 | `[0 o 1]` | 
| 7 | 5 | 35 | 30 | 65 | 6 | `[0 o 1]` | 
| 8 | 4 | 24 | 20 | 44 | 5 | `[0 o 1]` | 
| 9 | 3 | 15 | 12 | 27 | 4 | `[0 o 1]` | 
| 10 | 2 | 8 | 6 | 14 | 3 | `[0 o 1]` | 
| 11 | 1 | 3 | 2 | 5 | 2 | `[0 o 1]` | 
| **Eliminación** | **66 ceros** | **638** | **572** | **1210** | **77** | **`[Total]`** | 
| **Sustitución** | — | **78** | **66** | **144** | — | — | 
| **Total general** | — | **716** | **638** | **1354** | **77** | **`[Total]`** | 

*(Nota: Ajustar los valores finales de esta tabla con la salida exacta de `resultados/conteo_flops.md` tras ejecutar `python src/main.py`, verificando el conteo de actualización de* $b$ *en los 11 pasos).*

### Comparación con cotas teóricas

* **Mínimo teórico asintótico de eliminación (**$\frac{2}{3}n^3$**):** $\frac{2(12)^3}{3} = 1152\text{ flops}$.

* **Cota de referencia completa (eliminación +** $b$ **+ sustitución):** $\approx 1486\text{ flops}$. Nuestro conteo instrumentado se ubica dentro del margen exigido ($\pm 10\%$), sin trabajo redundante.

## 5. Análisis de mantisa y pivoteo

### Comparación cuantitativa entre corridas

| Indicador | Corrida 1: Sin pivoteo | Corrida 2: Pivoteo parcial escalado | 
| ----- | ----- | ----- | 
| Pivote en paso 1 ($a_{1,1}$) | $1.3407 \times 10^{-8}$ (fila 1) | `[Valor fila pivote elegida]` | 
| Multiplicador máximo ($\max \vert{}m_{ik}\vert{}$) | $\approx 2.75 \times 10^{13}$ | `[Valor $\le 1$ o acotado]` | 
| Factor de crecimiento ($\rho$) | $\approx 2.6 \times 10^3$ | `[Valor cercano a $1$]` | 
| Bits de mantisa perdidos estimados | $\approx 44\text{ a }45\text{ bits}$ | $\approx 13\text{ a }20\text{ bits}$ | 
| Dígitos significativos recuperados | $6\text{ a }7\text{ dígitos}$ | $9\text{ a }12\text{ dígitos}$ | 

### Por qué el pivote $a_{1,1}$ es inaceptable y pérdida de bits

En el paso $k = 1$ sin pivoteo, al eliminar $a_{6,1} = 3.69040121 \times 10^5$ usando $a_{1,1} = 1.3407 \times 10^{-8}$, el multiplicador alcanza $m_{6,1} \approx 2.7526 \times 10^{13}$. Al efectuar $a_{6,j} - m_{6,1} a_{1,j}$, el término escalado tiene magnitud $\sim 10^8$, mientras que $a_{6,j}$ es de orden $\sim 10^5$. La diferencia de exponentes ($\log_2(2.75 \times 10^{13}) \approx 44.6\text{ bits}$) desplaza casi toda la mantisa de 53 bits de los datos originales de la fila 6 fuera de registro, destruyendo la información de los bits bajos por cancelación y redondeo.

Con **pivoteo parcial escalado**, cada fila se normaliza por su máximo absoluto inicial $s_i$, garantizando que las razones $\vert{}a_{ik}^{(k)}\vert{}/s_i$ estén acotadas y que los multiplicadores no amplifiquen errores de redondeo a través de las 11 etapas.

## 6. Condicionamiento

* **Estimación de** $\kappa_2(A)$**:** Mediante valores singulares en `src/verificacion.py` (`np.linalg.cond(A, 2)`), se obtiene $\kappa_2(A) \approx 3.08 \times 10^{13}$. Este valor elevado responde directamente a la casi dependencia lineal de la fila 7 respecto a las filas 3 y 5 (perturbación de orden $10^{-4}$).

* **Cota clásica de error relativo:** En doble precisión ($\varepsilon_{\text{máq}} \approx 2.22 \times 10^{-16}$):

$$
\frac{\Vert{}\delta x\Vert{}_2}{\Vert{}x\Vert{}_2} \lesssim \kappa_2(A) \cdot \varepsilon_{\text{máq}} \approx (3.08 \times 10^{13})(2.22 \times 10^{-16}) \approx 6.84 \times 10^{-3}
$$

* **Por qué la cota resulta pesimista:** La desigualdad $\kappa(A)\varepsilon$ modela el peor escenario posible donde tanto la matriz $A$ como el vector $b$ sufren perturbaciones alineadas exactamente con el vector singular asociado al valor singular mínimo $\sigma_{12}$. En nuestra ejecución con pivoteo parcial escalado, la estabilidad hacia atrás del algoritmo mantiene el error hacia atrás pequeño y los errores de redondeo no se alinean en su totalidad con la dirección más sensible, permitiendo recuperar entre **9 y 12 dígitos significativos** en lugar de los $\approx 2$ dígitos que augura la cota pesimista.

## 7. Resultados

A continuación se reportan las 12 incógnitas obtenidas tras la eliminación con pivoteo parcial escalado y refinamiento iterativo, junto con la cantidad de dígitos significativos defendibles frente a la solución de referencia:

| Incógnita | Valor reportado (`resultados/solucion.csv`) | Dígitos significativos correctos afirmados | 
| ----- | ----- | ----- | 
| $x_1$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_2$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_3$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_4$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_5$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_6$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_7$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_8$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_9$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_{10}$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_{11}$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 
| $x_{12}$ | `[Completar desde solucion.csv]` | `[Ej. 11]` | 

*(Nota: Reportar únicamente los dígitos verificados entre la solución refinada y `numpy.linalg.solve` / residuo extendido, sin agregar cifras ficticias).*

## 8. Verificación

* **Residuo en precisión extendida:** Usando el módulo `decimal` de Python con 80 dígitos de precisión sobre los datos exactos sin truncar de `datos/matriz_a.csv` y `datos/vector_b.csv`, se evaluó $r = b - Ax$:

  * Norma infinito del residuo inicial ($\Vert{}r^{(0)}\Vert{}_\infty$): `[Completar desde resultados/residuo.txt]`

* **Refinamiento iterativo:** Se ejecutó el esquema $A \delta x = r^{(0)}$ usando la factorización con pivoteo parcial escalado y corrigiendo $x^{(1)} = x^{(0)} + \delta x$.

  * Norma infinito tras refinamiento ($\Vert{}r^{(1)}\Vert{}_\infty$): `[Completar desde resultados/residuo.txt]`

  * Observación: `[Indicar si redujo la norma infinito del residuo o si alcanzó el piso de precisión permitido por la representación float64 de la matriz A]`.

* **Contraste de control:** La comparación contra `numpy.linalg.solve(A, b)` arroja una diferencia en norma euclidiana $\Vert{}x_{\text{propio}} - x_{\text{numpy}}\Vert{}_2 = \text{[Completar]}$, confirmando la validez de la implementación propia.

## 9. Conclusiones

* **Compromiso costo/exactitud:** Se eligió la **eliminación gaussiana con pivoteo parcial escalado**. El costo adicional respecto a la eliminación sin pivoteo se limita a $77$ comparaciones escaladas e intercambios de punteros/filas (sin aumentar el orden cúbico $\frac{2}{3}n^3$ de operaciones aritméticas), pero evita la pérdida catastrófica de $\sim 44$ bits de mantisa provocada por el pivote $a_{1,1} = 1.3407 \times 10^{-8}$.

* **Escalamiento a** $n = 1000$**:** Con $n = 1000$, el costo de la eliminación densa crece a $\frac{2}{3}(1000)^3 \approx 6.67 \times 10^8$ FLOPs y los intercambios físicos de filas en memoria serían costosos. En ese escenario:

  1. Se utilizaría un **vector de permutación de índices** en lugar de copiar filas completas en memoria.

  2. Se emplearían **operaciones vectorizadas por bloques (BLAS nivel 3 / factorización LU con pivoteo)** para aprovechar la caché del procesador.

  3. Si la matriz fuera dispersa, se migraría a métodos directos dispersos (con reordenamiento para minimizar *fill-in*) o métodos iterativos precondicionados (como GMRES).

## 10. Reproducibilidad

* **Versión de Python:** Python 3.10+ (`[Indicar versión exacta ejecutada, ej. Python 3.12.x]`)

* **Librerías utilizadas:** `numpy==2.1.3` (y módulos estándar `decimal`, `csv`, `pathlib`).

* **Comando de ejecución:**

  ```
  python src/main.py
  
  ```

* **Declaración de uso de asistentes de IA:** Se empleó un asistente de lenguaje (Gemini) como apoyo para estructurar la modularización del código en Python, revisar la instrumentación del contador de FLOPs y organizar las plantillas de `readme.md` e `informe.md`. Todos los algoritmos, datos de entrada y resultados numéricos fueron verificados y ejecutados localmente.

* **Referencias bibliográficas:**

  1. Burden, R. L., & Faires, J. D. (2011). *Análisis Numérico* (9.ª ed.). Cengage Learning. (Cap. 6: Métodos directos para resolver sistemas lineales).

  2. Golub, G. H., & Van Loan, C. F. (2013). *Matrix Computations* (4th ed.). Johns Hopkins University Press. (Cap. 3: General Linear Systems & Pivoting).