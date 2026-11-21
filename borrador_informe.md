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

En el paso k = 1 sin pivoteo, al eliminar $a_6,1$ = 3.69040121 x 10^5 usando $a_1,1$ = 1.3407 x 10^-8, el multiplicador alcanza $m_6,1$ ≈