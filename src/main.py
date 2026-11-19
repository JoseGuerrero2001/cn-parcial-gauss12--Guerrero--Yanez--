from pathlib import path
import csv
import numpy as np

from conteo import contadorflops
from gauss import eliminacion_gaussiana,
sustitucion_regresiva
from verificacion import (
    estimar_condicionamiento,
    calcular_residuo_extendido,
    refinamiento_iterativo,
    control_biblioteca
)