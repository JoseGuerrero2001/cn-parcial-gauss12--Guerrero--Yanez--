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

    
        pass




