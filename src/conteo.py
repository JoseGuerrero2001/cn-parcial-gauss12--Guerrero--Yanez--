#Extencion contador Flops
#Instrumento simple del costo operacional de la eliminacion gausssiana y sustitucion regresiva

class ContadorFlops:

    def __init__(self , convencion: str = "1 operacion aritmetica elemental = 1 flop") -> None:

        self.convencion = convencion
        # Diccionario por paso k: {1: {"mult_div": 0, "suma_resta": 0, "comp_pivote": 0, "intercambios": 0}, ...}
        self.pasos: dict[int, dict[str, int]] = {}


        # Contadores para la sustitución regresiva
        self.sust_mult_div: int = 0
        self.sust_suma_resta: int = 0


        # Contadores globales del sobrecosto de pivoteo
        self.total_comp_pivote: int = 0
        self.total_intercambios: int = 0


    def _asegurar_paso(self, paso: int) -> dict[str, int]:
        if paso not in self.pasos:
            self.pasos[paso] = {
                "mult_div": 0,
                "suma_resta": 0,
                "comp_pivote": 0,
                "intercambios": 0,
            }
        return self.pasos[paso]


    def registrar_mult_div(self, paso: int | None, cantidad: int = 1) -> None:
        if paso is None:
            self.sust_mult_div += cantidad
        else:
            self._asegurar_paso(paso)["mult_div"] += cantidad

    def registrar_suma_resta(self, paso: int | None, cantidad: int = 1) -> None:
        if paso is None:
            self.sust_suma_resta += cantidad
        else:
            self._asegurar_paso(paso)["suma_resta"] += cantidad

    def registrar_comparacion_pivote(self, paso: int, cantidad: int = 1) -> None:
        self._asegurar_paso(paso)["comp_pivote"] += cantidad
        self.total_comp_pivote += cantidad

    def registrar_intercambio_fila(self, paso: int, cantidad: int = 1) -> None:
        self._asegurar_paso(paso)["intercambios"] += cantidad
        self.total_intercambios += cantidad

        pass




