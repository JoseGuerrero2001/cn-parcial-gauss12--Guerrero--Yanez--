# Conteo de Operaciones (FLOPs)

## Sin mivoteo

- **Convención declarada:** `1 operacion aritmetica elemental = 1 flop`
- **Dimensión (n):** 12
- **Minimo teórico eliminación (2n^3/3):** 1152.00 flops
- **Cota de referencia total:** ~1486 flops

### Desglose por paso (Eliminacion hacia adelante)

| Paso k | Mult / Div | Sumas / Restas | Subtotal FLOPs | Comp. pivote | Intercambios fila |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 143 | 132 | 275 | 0 | 0 |
| 2 | 120 | 110 | 230 | 0 | 0 |
| 3 | 99 | 90 | 189 | 0 | 0 |
| 4 | 80 | 72 | 152 | 0 | 0 |
| 5 | 63 | 56 | 119 | 0 | 0 |
| 6 | 48 | 42 | 90 | 0 | 0 |
| 7 | 35 | 30 | 65 | 0 | 0 |
| 8 | 24 | 20 | 44 | 0 | 0 |
| 9 | 15 | 12 | 27 | 0 | 0 |
| 10 | 8 | 6 | 14 | 0 | 0 |
| 11 | 3 | 2 | 5 | 0 | 0 |

### Resumen Global

| Etapa | Mult / Div | Sumas / Restas | Total FLOPs |
| :--- | :---: | :---: | :---: |
| Eliminacion hacia adelante (incluye b) | 638 | 572 | 1210 |
| Sustitucion regresiva | 78 | 66 | 144 |
| **Total aritmetico** | **716** | **638** | **1354** |

- **Sobrecosto de pivoteo (comparaciones):** 0
- **Intercambios de fila realizados:** 0

---

## Con Pivoteo pracial Escalado

- **Convención declarada:** `1 operacion aritmetica elemental = 1 flop`
- **Dimensión (n):** 12
- **Minimo teórico eliminación (2n^3/3):** 1152.00 flops
- **Cota de referencia total:** ~1486 flops

### Desglose por paso (Eliminacion hacia adelante)

| Paso k | Mult / Div | Sumas / Restas | Subtotal FLOPs | Comp. pivote | Intercambios fila |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 143 | 132 | 275 | 12 | 1 |
| 2 | 120 | 110 | 230 | 11 | 0 |
| 3 | 99 | 90 | 189 | 10 | 1 |
| 4 | 80 | 72 | 152 | 9 | 1 |
| 5 | 63 | 56 | 119 | 8 | 1 |
| 6 | 48 | 42 | 90 | 7 | 1 |
| 7 | 35 | 30 | 65 | 6 | 1 |
| 8 | 24 | 20 | 44 | 5 | 1 |
| 9 | 15 | 12 | 27 | 4 | 1 |
| 10 | 8 | 6 | 14 | 3 | 0 |
| 11 | 3 | 2 | 5 | 2 | 0 |

### Resumen Global

| Etapa | Mult / Div | Sumas / Restas | Total FLOPs |
| :--- | :---: | :---: | :---: |
| Eliminacion hacia adelante (incluye b) | 638 | 572 | 1210 |
| Sustitucion regresiva | 78 | 66 | 144 |
| **Total aritmetico** | **716** | **638** | **1354** |

- **Sobrecosto de pivoteo (comparaciones):** 77
- **Intercambios de fila realizados:** 8
