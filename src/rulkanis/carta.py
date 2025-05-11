from rulkanis.datos_rulkanis import nomenclaturas as _nomenclaturas

class Carta:
    def __init__(self, nombre, nomenclatura, nivel):
        self.nombre = nombre
        self.nomenclatura = nomenclatura
        self.nivel = nivel
        self.tipo = self.definir_tipo()
        self.categoria = self.obtener_categoria()

    def definir_tipo(self):
        uni = self.nombre.upper()
        if "AZAR" in uni:
            return "AZAR"
        elif "CERTERO" in uni:
            return "CERTERO"
        return "NORMAL"

    def accion_principal(self):
        return self.nomenclatura.split("+")[0].strip()
    
    def obtener_categoria(self):
        """
        Obtiene la categoría de una carta basada en su código de acción principal.
        La función recupera el código de acción principal de la carta, lo procesa 
        eliminando espacios en blanco y convirtiéndolo a mayúsculas, y luego lo 
        compara con una lista predefinida de nomenclaturas. Si se encuentra una 
        coincidencia, se devuelve la categoría correspondiente; de lo contrario, 
        se devuelve None.

        Args:
            carta (Carta): Una instancia de la clase Carta que representa la carta 
                        cuya categoría se desea determinar.
            str o None: La categoría de la carta si se encuentra una coincidencia 
                        en las nomenclaturas; de lo contrario, None.
        """
        codigo = self.accion_principal().strip().upper()
        for n in _nomenclaturas:
            if n['codigo'] == codigo:
                return n['categoria']
        return None

    def __repr__(self):
        return f"{self.nombre} (Nivel {self.nivel}, Tipo: {self.tipo})"


