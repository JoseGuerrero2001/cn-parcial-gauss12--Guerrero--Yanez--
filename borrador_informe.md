Informe Técnico: Eliminación Gaussiana con el Mínimo costo operacional y 
Máxima Exactitud de Mantisa

1. Identificaciones

_ Estudiantes: [Ricardo Yanez], [José Armando Guerrero Castillo]
_ Asignatura: Computación Numérica (INF-321) - Ingeniería Civil Informática,
Universidad Católica del Maule.
_ Docentes: Juan Manuel Cabezas Contardo - Pedro Pesante
_ Fecha y lugar: 20 de Noviembre de 2026, Talca. 
_ Repositorio Git: []

2.- Planteamiento

El problema consiste en resolver un sistema lineal denso Ax = b 
de dimensión n = 12(144 entradas no nulas en A) utilizando eliminación gaussiana en aritmética 
de punto flotante IEEE 754 de doble precisión (float64, mantisa de 53 bits ε máq ≈ 2.22 x 10^-16).

La dificultad numérica del sistema proviene de tres factores estructurales presentes en los datos:

1- Disparidad extrema de escalas entre filas: Las filas de A presentan magnitudes que abarcan trece 
órdenes de magnitud, desde elementos del orden de 10^-8 y 10^-5 (filas 1, 5 y 9) hasta entradas 
de orden 10^5 (fila 6). Al combinar filas sin escalar, el alineamiento de exponentes desplaza
los bits menos significativos del operando pequeno fuera de la mantisa de 53 bits.

2- Pivote inicial minúsculo: La entrada a1,1 = 1.3407 x 10^-8 es doce órdenes de magnitud menor
que a2,1 = 1.19229739 x 10^4 y trece órdenes menor que a6,1 = 3.69040121 x 10^5, lo que provoca
multiplicadores gigantescos si no se permutan filas.

3- Casi dependencia lineal oculta: La fila 7 se encuentra a una perturbación de orden 10^-4
de ser combinación lineal de las filas 3 y 5.
Aunque det(A) ≈ 1.3646 x 10^9 ≠ 0, esta cercanía a la singularidad eleva el número de condición
a k2(A) ≈ 3.08 x 10^13, volviendo el sistema altamente sensible a perturbaciones de redondeo.

3.- Estrategia de Eliminación

Para alcanzar el mínimo costo operacional en una matriz densa sin ceros, la implementación en
src/gauss.py sigue estrictamente el esquema de eliminación hacia adelante en n-1 = 11 etapas 
seguido de sustitución regresiva:

- Cálculo único del multiplicador: En cada paso k ε {1,...,11} y para cada
fila i>k, el multiplicador m ik = a^(k) ik/a^(k) kk se calcula una sola vez y se almacena en memoria para actualizar toda la fila
i y el término independiente b i. No se recalcula por columna.
- Barrido exclusivo sobre la submatriz activa: Dado que los elementos a ik (i>k) quedan anulados por construcción, el bucle interno de actualización recorre
únicamente las columnas j ε {k+1,...,n}, evitando operaciones redundantes sobre la subdiagonal ya eliminada.
- Factorización única sin inversión: Se trabaja directamente sobre una copia de a y b sin construir A^-1
- Pivoteo parcial escalado: Antes de eliminar en el paso k, se calcula el factor de escala inicial de cada fila s i = max 1≤j≤n |aij| y se selecciona la fila pivote p ≥ k
que maximiza la razón $|(a_(pk)^(k))|/s_p$. Esto neutraliza las diferencias de escala entre filas antes de dividir.

4.- Conteo de operaciones:

Convención declarada:

- 1 FLOP = 1 operación aritmética elemental en punto flotante (suma, resta, multiplicación o división).
- Las comparaciones de búsqueda de pivote y los intercambios de fila se contabilizan por separado como
sobrecosto de estabilidad, sin mezclarlos con los FLOP's aritméticos.
- El conteo se extrae directamente de la instrumentación en src/conteo.py (ContadorFlops).

Tabla paso a paso (n = 12)


Comparación con cotas teóricas
-Mínimo teórico asintótico de eliminación $((2/3)n^3):(2(12)^3)/3=1152 flops.$
-Cota de referencia completa (eliminación + b + sustitución): ≈ 1486 flops. Nuestro conteo instrumentado se ubica dentro del margen
exigido $(±10%)$, sin trabajo redundante.

5.- Análisis de mantisa y pivoteo

Comparación cuantitativa entre corridas

Indicador Corrida 1: Sin pivoteo  Corrida 2: Pivoteo parcial escalado


Por qué el pivote $a_1,1$ es inaceptable y pérdida de bits

En el paso k = 1 sin pivoteo, al eliminar $a_6,1$ = 3.69040121 x 10^5 usando $a_1,1$ = 1.3407 x 10^-8, el multiplicador alcanza $m_6,1 ≈ 2.7526 x 10^13$.
 Al efectuar $a_6,j$ $a_1,j$, el término escalado tiene magnitud $10^8$, mientras que $a_6,j$ es de orden 10^5. 
 La diferencia de exponentes $(log_2 (2.75 x 10^13)$ ≈ 44.6 bits) desplaza casi toda la mantisa de 53 bits de los datos originales de la fila 6 fuera de registro,
 destruyendo la información la información de los bits bajos por cancelación y redondeo.

 Con pivoteo parcial escalado, cada fila se normaliza por su máximo absoluto inicial $s_i$, garantizando que las razones $|a^(k)_(ik)|/s_i$ estén acotadas y que los multiplicadores
 no amplifiquen errores de redondeo a través de las 11 etapas.

 6.- Condicionamiento

 - Estimación de $k_2$(A): Mediante valores singulares en src/verificacion.py (np.linalg.cond(A, 2)), se obtiene $k_2$(A) ≈ $3.08 x 10^13$. Este valor elevado responde directamente
 a la casi dependencia lineal de la fila 7 respecto a las filas 3 y 5 (perturbación de orden 10^-4).

 - Cota clásica de error relativo: En doble precisión ($ε_máq ≈ 2.22 x 10^-16$):

 $(||δx||_2)/(||x||_2) < k_2(A).ε_máq ≈ (3.08 x 10 ^13)(2.22 x 10^-16) ≈ 6.84 x 10^-3$

 - Por qué la cota resulta pesimista: La desigualdad $k(A)ε modela el peor escenario posible donde tanto la matriz A como el vector b
 sufren perturbaciones alineadas exactamente con el vector singular asociado al valor singular mínimo $\sigma_{12}$. 
 En nuestra ejecución con pivoteo parcial escalado, la estabilidad hacia atrás del algoritmo
 mantiene el error hacia atrás pequeño y los errores de redondeo no se alinean en su totalidad con la dirección más sensible, permitiendo
 recuperar entre 9 y 12 dígitos significativos en lugar de los ≈ 2 dígitos que augura la cota pesimista.

 7.- Resultados
 A continuación se reportan las 12 incógnitas obtenidas tras la eliminación con pivoteo parcial
 escalado y refinamiento iterativo, junto con la cantidad de dígitos significativos defendibles frente a la solución de referencia:


 8.- Verificación

 - Residuo en precisión extendida: Usando el módulo decimal de Python con 80 dígitos de precisión sobre los datos exactos sin truncar de "datos/matriz_a.csv"  y "datos/vector_b.csv",
 se evaluó $r = b - Ax:$

 - Norma infinito del residuo inicial $(||r^(0)||_∞)$: 

 -Refinamiento iterativo: Se ejecutó el esquema $Aδx = r^(0)$ usando la factorización con pivoteo parcial escalado y corrigiendo $x^(1) = x^(0) + δx$.
 - Norma infinito tras refinamiento $(||r^(1)||_∞)$:

 - Observación:

 -Contraste de control: La comparación contra numpy.linalg.solve(a, b) arroja una diferencia
 en norma euclidiana $||x_propio - x_numpy||_2 $ = , confirmando la validez del a implementación propia.

 9.- Conclusiones:

 - Compromiso costo/exactitud: Se eligió la eliminación gaussiana con pivoteo parcial escalado.
 El costo adicional respecto a la eliminación sin pivoteo se limita a 77 comparaciones escaladas e
 intercambios de punteros/filas (sin aumentar el orden cúbico $(2/3)n^3$ de operaciones aritméticas), pero
 evita la pérdida catastrófica de 44 bits de mantisa provocada por el pivote $a_1,1 = 1.3407 x 10^-8$

 - Escalamiento a n = 1000: Con n = 1000, el costo de la eliminación densa crece a $(2/3)(1000)^3 ≈ 6.67 x 10^8$ FLOP's y los intercambios físicos de filas 
 de filas en memoria serían costosos. En ese escenario: 

 1- Se utilizaría un vector de permutación de índices en lugar de copiar filas completas en 
 memoria. 
 2- Se emplearían operaciones vectorizadas por bloques (BLAS nivel 3/ factorización LU con pivoteo) para aprovechar la caché del procesador.

 3- Si la matriz fuera dispersa, se migraría a métodos directos dispersos (con reordenamiento para minimizar fill-in) o métodos iterativos precondicionados.

 10.- Reproducibilidad

 - Versión de Python: Python 3.10 + Python 3.14.10
 - Librerías utilizadas: numpy==2.1.3 (y módulos estándar decimal, csv, Pathlib).
 - Comando de ejecución:

    python src/main.py

- Declaración de uso de asistentes de IA:  El uso de IA se establecio principalmente para realizar
borradores y códigos de referencia, lo que ayudo a guiar la idea general del trabajo.
Procedimos a observar su funcionamiento, y fue tanto modificado como adaptado a nuestras necesidades.
Finalmente, fue usado como último recurso cuando surgieron errores en líneas específicas y dar algunos retoques finales.
