# reglas.py
# Implementación de reglas y handlers para Rulkanis
import random
from rulkanis.datos_rulkanis import nomenclaturas as _nomenclaturas
from rulkanis.jugador import Jugador
from rulkanis.carta import Carta

def determinar_exito_carta(carta: Carta, actual: Jugador):
    """
    Determina si una carta tiene éxito o falla al ser jugada por un jugador.

    Args:
        carta (Carta): La carta que se está evaluando.
        actual (Jugador): El jugador que está jugando la carta.

    Returns:
        None: La función no retorna un valor, pero registra un evento con el resultado
        de la evaluación de la carta (éxito o fallo) y, si aplica, el valor del dado lanzado.

    Notas:
        - Si la carta es de tipo "AZAR", se lanza un dado para determinar el éxito.
        - El límite para el éxito del dado depende de si el jugador tiene suerte.
        - El evento generado incluye el nombre de la carta, el resultado (éxito o fallo),
          y el valor del dado si corresponde.
    """
    exito = True
    dado = "-"
    if carta.tipo == "AZAR":
        d = actual.lanzar_dado()
        limite = 4 if actual.tiene_suerte() else 6
        exito = d >= limite
        dado = d

    resultado = "Éxito" if exito else "Fallo"
    evento = f"{carta.nombre} ({resultado}"
    if dado != "-":
        evento += f", dado={dado}"
    evento += ")"

    return exito, evento, resultado, dado

# Obtener categoría principal de la carta (ataque, defensa, etc.)
def obtener_categoria(carta: Carta):
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
    codigo = carta.accion_principal().strip().upper()
    for n in _nomenclaturas:
        if n['codigo'] == codigo:
            return n['categoria']
    return None

# Aplica daño considerando esquiva y defensa
def aplicar_dano(jugador: Jugador, cantidad: int):
    # Esquiva
    if jugador.estado.get('esquiva', False):
        jugador.estado['esquiva'] = False
        return "Daño esquivado"
    # Defensa
    def_val = jugador.estado.get('defensa', 0)
    if def_val >= cantidad:
        jugador.estado['defensa'] = def_val - cantidad
        return f"{cantidad} absorbido por defensa (defensa ahora {jugador.estado['defensa']})"
    # Resto a vida
    restante = cantidad - def_val
    jugador.estado['defensa'] = 0
    jugador.vida -= restante
    return f"{def_val} absorbido, {restante} a vida (vida ahora {jugador.vida})"

# Handlers de acciones específicas
def accion_AL(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    evento = aplicar_dano(oponente, 1)
    eventos.append(f"Ataque Ligero: {evento}")

def accion_AN(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    evento = aplicar_dano(oponente, 2)
    eventos.append(f"Ataque Normal: {evento}")

def accion_AC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    evento = aplicar_dano(oponente, 3)
    eventos.append(f"Ataque Crítico: {evento}")

def accion_SA(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    d = actual.lanzar_dado()
    if d >= 6:
        oponente.estado['sangrado'] = 3
        evento = aplicar_dano(oponente, 1)
        eventos.append(f"Sangrado Azar: aplicado (dado={d}, 1×3 turnos)")
    else:
        eventos.append(f"Sangrado Azar: fallido (dado={d})")


def accion_SC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    oponente.estado['sangrado'] = 3
    evento = aplicar_dano(oponente, 1)
    eventos.append("Sangrado Certero: aplicado (1×3 turnos)")


def accion_FA(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    d = actual.lanzar_dado()
    if d >= 6:
        oponente.estado['fuego'] = 3
        evento = aplicar_dano(oponente, 1)
        eventos.append(f"Fuego Azar: aplicado (dado={d}, 1×3 turnos)")
    else:
        eventos.append(f"Fuego Azar: fallido (dado={d})")


def accion_FC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    oponente.estado['fuego'] = 3
    evento = aplicar_dano(oponente, 1)
    eventos.append("Fuego Certero: aplicado (1×3 turnos)")


def accion_BD(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.estado['defensa'] += 1
    eventos.append("Bufo Defensa: +1 defensa")


def accion_BDN(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.estado['defensa'] += 2
    eventos.append("Bufo Defensa Normal: +2 defensa")


def accion_BDF(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.estado['defensa'] += 3
    eventos.append("Bufo Defensa Fuerte: +3 defensa")


def accion_BVP(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.vida += 1
    eventos.append(f"Bufo Vida Pequeño: +1 vida (vida ahora {actual.vida})")


def accion_BVM(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.vida += 2
    eventos.append(f"Bufo Vida Mediano: +2 vida (vida ahora {actual.vida})")


def accion_BVG(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.vida += 3
    eventos.append(f"Bufo Vida Grande: +3 vida (vida ahora {actual.vida})")


def accion_PA(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    d = actual.lanzar_dado()
    if d >= 6:
        oponente.estado['paralizado'] = 2
        eventos.append(f"Paralizar Azar: aplicado (dado={d}, 2 turnos)")
    else:
        eventos.append(f"Paralizar Azar: fallido (dado={d})")


def accion_PC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    oponente.estado['paralizado'] = 2
    eventos.append("Paralizar Certero: aplicado (2 turnos)")


def accion_CA(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    d = actual.lanzar_dado()
    if d >= 6:
        oponente.estado['congelado'] = 1
        eventos.append(f"Congelar Azar: aplicado (dado={d}, salta turno)")
    else:
        eventos.append(f"Congelar Azar: fallido (dado={d})")


def accion_CC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    oponente.estado['congelado'] = 1
    eventos.append("Congelar Certero: aplicado (salta turno)")


def accion_BLA(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    for s in ['sangrado', 'fuego', 'paralizado', 'congelado']:
        actual.estado[s] = 0
    eventos.append("Limpieza: estados negativos eliminados")


def accion_BS(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.suerte_turnos = 4
    eventos.append("Bufo Suerte: activado (4 turnos, limite=4)")


def accion_EA(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    d = actual.lanzar_dado()
    if d >= 6:
        actual.estado['esquiva'] = True
        eventos.append(f"Esquivar Azar: activado (dado={d})")
    else:
        eventos.append(f"Esquivar Azar: fallido (dado={d})")


def accion_EC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.estado['esquiva'] = True
    eventos.append("Esquivar Certero: activado")


def accion_RC(carta: Carta, actual: Jugador, oponente: Jugador, eventos: list):
    actual.robar(1)
    oponente.robar(1)
    eventos.append("Robo Carta: ambos roban 1 carta")

# Mapeo de códigos a handlers
HANDLERS = {
    'AL': accion_AL, 'AN': accion_AN, 'AC': accion_AC,
    'SA': accion_SA, 'SC': accion_SC,
    'FA': accion_FA, 'FC': accion_FC,
    'BD': accion_BD, 'BDN': accion_BDN, 'BDF': accion_BDF,
    'BVP': accion_BVP, 'BVM': accion_BVM, 'BVG': accion_BVG,
    'PA': accion_PA, 'PC': accion_PC,
    'CA': accion_CA, 'CC': accion_CC,
    'BLA': accion_BLA, 'BS': accion_BS,
    'EA': accion_EA, 'EC': accion_EC,
    'RC': accion_RC
}


# Aplica todos los handlers de una carta combinada
def aplicar_carta(
    carta: Carta, jugador_actual: Jugador, jugador_oponente: Jugador, eventos: list
):
    for code in carta.nomenclatura.split('+'):
        accion = HANDLERS.get(code.strip().upper())
        if accion:
            accion(carta, jugador_actual, jugador_oponente, eventos)
