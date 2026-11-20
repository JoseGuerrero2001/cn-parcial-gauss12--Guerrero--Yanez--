El Pivote: Eliminacion gaussiana en Sistemas densos tipo 12 x 12

En el presente código, se presencia una implementacion en Python de eliminacion gaussiana densa (con dos casos, sin pivoteo y con pivoteo parcial escalado) con una instrumentación de FLOP's, control de mantisa
y verificación en precisión extendida para un sistema lineal mal condicionado que posee 12 incógnitas.

Autoría y asignatura:
_ Estudiantes: [Ricardo Yañez Vega], [José Armando Guerrero Castillo]
_ Asignatura: Computación Numérica (INF-321) - Ing. Civil Informática, Universidad Católica del Maule (UCM)
_ Docentes: Juan Manuel Cabezas Contardo, Pedro Pesante

Requisitos necesarios para ejecutarse:

_ Lenguaje: Python 3.10 o superior.

_ Instalación de dependencias:

pip install -r requirements.txt

Método de Ejecución:
Desde la raíz del repositorio, ejecuta el punto de entrada único:

python src/main.py

El comando procede a leer datos/matriz_a.csv y datos/vector_b.csv y genera automáticamente en resultados/ :
_ solucion.csv: incógnitas x1 . . . x12 sin pivoteo y refinadas con pivoteo parcial escalado.
_ traza_eliminacion.txt: matrices resultantes tras cada uno de los 11 pasos de eliminación para ambas corridas.
_ conteo_flops.md: desglose tabular de operaciones aritméticas y sobrecosto de pivoteo por paso.
_  residuo.txt: npumero de condición k2(A), vector residuo r = b - Ax en precisión extendida y su norma infinito.

Estructura de carpetas:

cn-parcial-gauss12-<yanez>/<guerrero>
|- readme.md            #Guía rápida de instalacion, ejecucion y resumen de resultados
|- informe.md           #Informe técnico y completo con análisis numérico, tablas y conclusiones
|- requirements.txt     #Dependencias con versión fija (numpy==2.1.3)
|- datos/               #Matriz a (12x12) y vector b (20 dígitos) en formato CSV exacto
|- src/                 #Código fuente modular (main.py, gauss.py, verificacion.py)
|- resultados/          #Salidas generadas automáticamente por main.py
|- .gitignore           #Exclusión de caché, entornos virtuales y archivos temporales

Resultados de forma resumida:

Incógnita | Valor obtenido (10 dígitos)
x1
x2
x3
x4
x5
x6
x7
x8
x9
x10
x11
x12

_ Total de FLOP's aritméticos: 1486 operaciones elementales (eliminación + actualización 
de b + sustitución regresiva), más 66 comparaciones de pivoteo.
_ Norma infinito del residuo (||b - Ax||∞): 


Documentación de elementos técnicos:

Aplicación académica:

Material Académico: Material desarrollado exclusivamente con fines únicamente académicos 
para la evaluación parcial de Computación Numérica (INF-321), en la Universidad Católica del Maule, Noviembre de 2026.
