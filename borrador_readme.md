# El Pivote: Eliminación Gaussiana en Sistema Denso 12×12

Implementación en Python de eliminación gaussiana densa (sin pivoteo y con pivoteo parcial escalado) con instrumentación de FLOPs, control de mantisa y verificación en precisión extendida para un sistema lineal mal condicionado de 12 incógnitas.

## Autoría y asignatura

* **Estudiantes:** [Nombre Estudiante 1], [Nombre Estudiante 2 (si aplica)]
* **Asignatura:** Computación Numérica (INF-321) — Ingeniería Civil Informática, Universidad Católica del Maule (UCM)
* **Docentes:** Juan Manuel Cabezas Contardo · Pedro Pesante

## Requisitos

* **Lenguaje:** Python 3.10 o superior.
* **Instalación de dependencias:**

```bash
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del repositorio, ejecuta el punto de entrada único:

```bash
python src/main.py
```

El comando lee `datos/matriz_a.csv` y `datos/vector_b.csv` y genera automáticamente en `resultados/`:
* `solucion.csv`: incógnitas $x_1 \dots x_{12}$ sin pivoteo y refinadas con pivoteo parcial escalado.
* `traza_eliminacion.txt`: matrices resultantes tras cada uno de los 11 pasos de eliminación para ambas corridas.
* `conteo_flops.md`: desglose tabular de operaciones aritméticas y sobrecosto de pivoteo por paso.
* `residuo.txt`: número de condición $\kappa_2(A)$, vector residuo $r = b - Ax$ en precisión extendida y su norma infinito.

## Estructura de carpetas

```text
cn-parcial-gauss12-<apellido>/
├─ readme.md        # Guía rápida de instalación, ejecución y resumen de resultados
├─ informe.md       # Informe técnico con análisis numérico, tablas y conclusiones
├─ requirements.txt # Dependencias con versión fija (numpy==2.1.3)
├─ datos/           # Matriz A (12x12) y vector b (20 dígitos) en formato CSV exacto
├─ src/             # Código fuente modular (main.py, gauss.py, conteo.py, verificacion.py)
├─ resultados/      # Salidas generadas automáticamente por main.py
└─ .gitignore       # Exclusión de caché, entornos virtuales y archivos temporales
```

## Resultado resumido

| Incógnita | Valor obtenido (10 dígitos) |
| :---: | :---: |
| $x_1$ | `[Completar al ejecutar main.py]` |
| $x_2$ | `[Completar al ejecutar main.py]` |
| $x_3$ | `[Completar al ejecutar main.py]` |
| $x_4$ | `[Completar al ejecutar main.py]` |
| $x_5$ | `[Completar al ejecutar main.py]` |
| $x_6$ | `[Completar al ejecutar main.py]` |
| $x_7$ | `[Completar al ejecutar main.py]` |
| $x_8$ | `[Completar al ejecutar main.py]` |
| $x_9$ | `[Completar al ejecutar main.py]` |
| $x_{10}$ | `[Completar al ejecutar main.py]` |
| $x_{11}$ | `[Completar al ejecutar main.py]` |
| $x_{12}$ | `[Completar al ejecutar main.py]` |

* **Total de FLOPs aritméticos:** 1486 operaciones elementales (eliminación + actualización de $b$ + sustitución regresiva), más 66 comparaciones de pivoteo.
* **Norma infinito del residuo ($\|b - Ax\|_\infty$):** `[Completar con valor de resultados/residuo.txt]`

## Documentación técnica

Para el análisis completo de error de redondeo, conteo paso a paso y condicionamiento, consultar el [informe técnico](informe.md).

## Uso académico

Material desarrollado exclusivamente con fines académicos para la evaluación parcial de Computación Numérica (INF-321), Universidad Católica del Maule, noviembre de 2026.