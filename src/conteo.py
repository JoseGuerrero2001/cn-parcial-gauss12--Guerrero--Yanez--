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


    def total_elim_mult_div(self) -> int:
        return sum(datos["mult_div"] for datos in self.pasos.values())

    def total_elim_suma_resta(self) -> int:
        return sum(datos["suma_resta"] for datos in self.pasos.values())

    def total_elim_flops(self) -> int:
        return self.total_elim_mult_div() + self.total_elim_suma_resta()

    def total_sust_flops(self) -> int:
        return self.sust_mult_div + self.sust_suma_resta

    def total_general_flops(self) -> int:
        return self.total_elim_flops() + self.total_sust_flops()

def generar_reporte_markdown(self, titulo_corrida: str, n: int = 12) -> str:
        minimo_teorico = (2 * (n ** 3)) / 3
        cota_referencia = 1486

        lineas = [
            f"## {titulo_corrida}",
            "",
            f"- **Convención declarada:** `{self.convencion}`",
            f"- **Dimensión (n):** {n}",
            f"- **Minimo teórico eliminación (2n^3/3):** {minimo_teorico:.2f} flops",
            f"- **Cota de referencia total:** ~{cota_referencia} flops",
            "",
            "### Desglose por paso (Eliminacion hacia adelante)",
            "",
            "| Paso k | Mult / Div | Sumas / Restas | Subtotal FLOPs | Comp. pivote | Intercambios fila |",
            "| :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for k in sorted(self.pasos.keys()):
            datos = self.pasos[k]
            subtotal = datos["mult_div"] + datos["suma_resta"]
            lineas.append(
                f"| {k} | {datos['mult_div']} | {datos['suma_resta']} | "
                f"{subtotal} | {datos['comp_pivote']} | {datos['intercambios']} |"
            )

        lineas.extend([
            "",
            "### Resumen Global",
            "",
            "| Etapa | Mult / Div | Sumas / Restas | Total FLOPs |",
            "| :--- | :---: | :---: | :---: |",
            f"| Eliminacion hacia adelante (incluye b) | {self.total_elim_mult_div()} | {self.total_elim_suma_resta()} | {self.total_elim_flops()} |",
            f"| Sustitucion regresiva | {self.sust_mult_div} | {self.sust_suma_resta} | {self.total_sust_flops()} |",
            f"| **Total aritmetico** | **{self.total_elim_mult_div() + self.sust_mult_div}** | **{self.total_elim_suma_resta() + self.sust_suma_resta}** | **{self.total_general_flops()}** |",
            "",
            f"- **Sobrecosto de pivoteo (comparaciones):** {self.total_comp_pivote}",
            f"- **Intercambios de fila realizados:** {self.total_intercambios}",
            "",
        ])

        return "\n".join(lineas)

        pass




