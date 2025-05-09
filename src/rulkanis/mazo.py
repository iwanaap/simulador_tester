import random
import numpy as np
from rulkanis.datos_rulkanis import cartas_accion, distribucion_equipamiento, equipamiento_sets_nominales
from rulkanis.carta import Carta


def construir_lista_cartas():
    """
    Construye una lista de objetos de tipo Carta a partir de una lista de diccionarios predefinida
    llamada 'cartas_accion'.

    Retorna:
        list: Una lista de objetos Carta, donde cada objeto se crea utilizando los valores de las
        claves 'nombre', 'nomenclatura' y 'nivel' de cada diccionario en 'cartas_accion'.
    """
    return [Carta(c["nombre"], c["nomenclatura"], c["nivel"]) for c in cartas_accion]


# ---------------------------------------------------------------------------
#  Construccion de mazo por el usuario
def seleccionar_pieza_equipamiento(pieza: str, sets_disponibles: dict):
    """
    Permite al usuario seleccionar una pieza específica de un conjunto disponible.

    Args:
        pieza (str): El nombre de la pieza que se desea seleccionar.
        sets_disponibles (dict): Un diccionario donde las claves son los nombres de los conjuntos
                                 y los valores son diccionarios que contienen las piezas disponibles.

    Returns:
        tuple: Una tupla que contiene:
            - key (str): El nombre del conjunto seleccionado.
            - valor (varios): El valor asociado a la pieza seleccionada dentro del conjunto.

    Raises:
        ValueError: Si la entrada del usuario no es un número válido o está fuera del rango.
    """
    print(f"\nSelecciona {pieza.upper()}:")
    nombres = list(sets_disponibles.keys())
    for i, nombre in enumerate(nombres):
        print(f"  {i+1}. {nombre}")
    while True:
        try:
            sel = int(input("Número del set: ")) - 1
            if 0 <= sel < len(nombres):
                key = nombres[sel]
                return key, sets_disponibles[key][pieza.upper()]
        except:
            print("Entrada inválida.")


def elegir_cartas_por_nivel(cartas_disponibles: list, nivel: int, cantidad: int):
    opciones = [carta for carta in cartas_disponibles if carta.nivel == nivel]
    seleccion: list = []
    print(f"\nCartas disponibles de nivel {nivel}:")
    for i, carta in enumerate(opciones):
        print(f"  {i+1}. {carta}")
    while len(seleccion) < cantidad:
        try:
            idx = int(input("Elige carta: ")) - 1
            if 0 <= idx < len(opciones):
                seleccion.append(opciones[idx])
        except:
            print("Entrada inválida.")
    return seleccion


def construir_mazo_combinado(nombre_jugador):
    print(f"\n--- {nombre_jugador.upper()} ---")
    todas = construir_lista_cartas()
    mazo = []
    origen = {}

    # Mapeo para que coincida con las claves de distribución

    for parte in ["ARMA", "BOTAS", "CASCO", "PECHERA", "GUANTES"]:
        set_name, noms = seleccionar_pieza_equipamiento(parte, equipamiento_sets_nominales)
        origen[parte] = set_name

        # Filtramos las cartas de ese set
        disp = [c for c in todas if c.nomenclatura in noms]

        # Obtenemos la distribución correcta usando la clave plural
        dist = distribucion_equipamiento.get(parte, {})

        for nivel, cantidad in dist.items():
            cand = [c for c in disp if c.nivel == nivel and c]
            elegidos = cand[:cantidad]
            mazo.extend(elegidos)

    # Ahora sí agregamos las 10 cartas extras
    print("\n--- Selección de 10 cartas adicionales ---")
    extras = {1:2, 2:2, 3:2, 4:2, 5:2}  # nivel: cantidad
    for nivel, cantidad in extras.items():
        mazo.extend(elegir_cartas_por_nivel(todas, nivel, cantidad))

    print(f"\nResumen del mazo de {nombre_jugador} (total {len(mazo)} cartas):")
    for c in mazo:
        print(" -", c)

    return mazo, origen


# ---------------------------------------------------------------------------
#  Construccion de mazo aleatorio
def seleccionar_pieza_random(pieza: str, sets_disponibles: dict):
    """
    Selecciona aleatoriamente un conjunto disponible y devuelve la pieza correspondiente.

    Args:
        pieza (str): El nombre de la pieza a buscar. Se convierte a mayúsculas para la búsqueda.
        sets_disponibles (dict): Un diccionario donde las claves son los nombres de los conjuntos
            y los valores son diccionarios que contienen las piezas disponibles en cada conjunto.

    Returns:
        tuple: Una tupla que contiene:
            - str: El nombre del conjunto seleccionado aleatoriamente.
            - Any: La pieza correspondiente dentro del conjunto seleccionado.
    
    Raises:
        KeyError: Si la pieza especificada no se encuentra en el conjunto seleccionado.
        IndexError: Si no hay conjuntos disponibles en el diccionario.
    """

    random_set = random.choice(list(sets_disponibles.keys()))
    return random_set, sets_disponibles[random_set][pieza.upper()]


def elegir_cartas_por_nivel_random(cartas_disponibles: list, nivel: int, cantidad: int):
    """
    Selecciona una cantidad específica de cartas al azar de un nivel dado.

    Args:
        cartas_disponibles (list): Lista de cartas disponibles para seleccionar.
        nivel (int): Nivel de las cartas que se desean seleccionar.
        cantidad (int): Cantidad de cartas a seleccionar.

    Returns:
        list: Una lista con las cartas seleccionadas al azar que cumplen con el nivel especificado.

    Raises:
        ValueError: Si la cantidad solicitada es mayor que el número de cartas disponibles del nivel especificado.
    """
    opciones = [carta for carta in cartas_disponibles if carta.nivel == nivel]
    seleccion: list = random.sample(opciones, cantidad)
    return seleccion

def construir_mazo_random(nombre_jugador, seed: int = None):

    # Fijar la semilla para reproducibilidad
    random.seed(seed)
    np.random.seed(seed)

    todas_cartas = construir_lista_cartas()
    mazo = []
    set_jugador = {}

    # Mapeo para que coincida con las claves de distribución

    for parte in ["ARMA", "BOTAS", "CASCO", "PECHERA", "GUANTES"]:
        nombre_set, nomenclaturas_disponibles = seleccionar_pieza_random(
            parte, equipamiento_sets_nominales
        )
        set_jugador[parte] = nombre_set

        # Filtramos las cartas de ese set
        disponibles = [
            carta
            for carta in todas_cartas
            if carta.nomenclatura in nomenclaturas_disponibles
        ]

        # Obtenemos la distribucion de cantidad de cartas por nivel para la pieza escogida
        distribucion_cartas_pieza = distribucion_equipamiento.get(parte, {})

        for nivel, cantidad in distribucion_cartas_pieza.items():
            cartas_pieza = [
                carta
                for carta in disponibles
                if carta.nivel == nivel and carta
            ]
            elegidos = np.random.choice(cartas_pieza, cantidad)
            mazo.extend(elegidos)
        
    # Agregamos 10 cartas extras aleatorias
    distribucion_extras = {1:2, 2:2, 3:2, 4:2, 5:2}  # nivel: cantidad
    for nivel, cantidad in distribucion_extras.items():
        mazo.extend(elegir_cartas_por_nivel_random(todas_cartas, nivel, cantidad))

    print(f"\nResumen del mazo de {nombre_jugador} (total {len(mazo)} cartas):")
    for c in mazo:
        print(" -", c)
    
    return mazo, set_jugador
