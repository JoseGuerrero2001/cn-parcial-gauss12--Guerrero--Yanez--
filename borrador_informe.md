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
de punto flotante IEEE 754 de doble precisión (float64, mantisa de 53 bitsεmáq ≈ 2.22 x 10^-16).

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

- Cálculo único del multiplicador: En cada paso k 
-
-
-
                                