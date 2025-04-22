# reglas.py
# Implementación de reglas y handlers para Rulkanis
import random
from datos_rulkanis import nomenclaturas as _nomenclaturas

# Lanzar dado de 10 caras (retorna entero 1–10)
def lanzar_dado():
    return random.randint(1, 10)

# Obtener categoría principal de la carta (ataque, defensa, etc.)
def obtener_categoria(carta):
    codigo = carta.accion_principal().strip().upper()
    for n in _nomenclaturas:
        if n['codigo'] == codigo:
            return n['categoria']
    return None

# Aplica daño considerando esquiva y defensa
def aplicar_dano(jugador, cantidad):
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
def accion_AL(carta, actual, oponente, eventos):
    evento = aplicar_dano(oponente, 1)
    eventos.append(f"Ataque Ligero: {evento}")

def accion_AN(carta, actual, oponente, eventos):
    evento = aplicar_dano(oponente, 2)
    eventos.append(f"Ataque Normal: {evento}")

def accion_AC(carta, actual, oponente, eventos):
    evento = aplicar_dano(oponente, 3)
    eventos.append(f"Ataque Crítico: {evento}")

def accion_SA(carta, actual, oponente, eventos):
    d = lanzar_dado()
    if d >= 6:
        oponente.estado['sangrado'] = 3
        evento = aplicar_dano(oponente, 1)
        eventos.append(f"Sangrado Azar: aplicado (dado={d}, 1×3 turnos)")
    else:
        eventos.append(f"Sangrado Azar: fallido (dado={d})")


def accion_SC(carta, actual, oponente, eventos):
    oponente.estado['sangrado'] = 3
    evento = aplicar_dano(oponente, 1)
    eventos.append("Sangrado Certero: aplicado (1×3 turnos)")


def accion_FA(carta, actual, oponente, eventos):
    d = lanzar_dado()
    if d >= 6:
        oponente.estado['fuego'] = 3
        evento = aplicar_dano(oponente, 1)
        eventos.append(f"Fuego Azar: aplicado (dado={d}, 1×3 turnos)")
    else:
        eventos.append(f"Fuego Azar: fallido (dado={d})")


def accion_FC(carta, actual, oponente, eventos):
    oponente.estado['fuego'] = 3
    evento = aplicar_dano(oponente, 1)
    eventos.append("Fuego Certero: aplicado (1×3 turnos)")


def accion_BD(carta, actual, oponente, eventos):
    actual.estado['defensa'] += 1
    eventos.append("Bufo Defensa: +1 defensa")


def accion_BDN(carta, actual, oponente, eventos):
    actual.estado['defensa'] += 2
    eventos.append("Bufo Defensa Normal: +2 defensa")


def accion_BDF(carta, actual, oponente, eventos):
    actual.estado['defensa'] += 3
    eventos.append("Bufo Defensa Fuerte: +3 defensa")


def accion_BVP(carta, actual, oponente, eventos):
    actual.vida += 1
    eventos.append(f"Bufo Vida Pequeño: +1 vida (vida ahora {actual.vida})")


def accion_BVM(carta, actual, oponente, eventos):
    actual.vida += 2
    eventos.append(f"Bufo Vida Mediano: +2 vida (vida ahora {actual.vida})")


def accion_BVG(carta, actual, oponente, eventos):
    actual.vida += 3
    eventos.append(f"Bufo Vida Grande: +3 vida (vida ahora {actual.vida})")


def accion_PA(carta, actual, oponente, eventos):
    d = lanzar_dado()
    if d >= 6:
        oponente.estado['paralizado'] = 2
        eventos.append(f"Paralizar Azar: aplicado (dado={d}, 2 turnos)")
    else:
        eventos.append(f"Paralizar Azar: fallido (dado={d})")


def accion_PC(carta, actual, oponente, eventos):
    oponente.estado['paralizado'] = 2
    eventos.append("Paralizar Certero: aplicado (2 turnos)")


def accion_CA(carta, actual, oponente, eventos):
    d = lanzar_dado()
    if d >= 6:
        oponente.estado['congelado'] = 1
        eventos.append(f"Congelar Azar: aplicado (dado={d}, salta turno)")
    else:
        eventos.append(f"Congelar Azar: fallido (dado={d})")


def accion_CC(carta, actual, oponente, eventos):
    oponente.estado['congelado'] = 1
    eventos.append("Congelar Certero: aplicado (salta turno)")


def accion_BLA(carta, actual, oponente, eventos):
    for s in ['sangrado', 'fuego', 'paralizado', 'congelado']:
        actual.estado[s] = 0
    eventos.append("Limpieza: estados negativos eliminados")


def accion_BS(carta, actual, oponente, eventos):
    actual.suerte_turnos = 4
    eventos.append("Bufo Suerte: activado (4 turnos, limite=4)")


def accion_EA(carta, actual, oponente, eventos):
    d = lanzar_dado()
    if d >= 6:
        actual.estado['esquiva'] = True
        eventos.append(f"Esquivar Azar: activado (dado={d})")
    else:
        eventos.append(f"Esquivar Azar: fallido (dado={d})")


def accion_EC(carta, actual, oponente, eventos):
    actual.estado['esquiva'] = True
    eventos.append("Esquivar Certero: activado")


def accion_RC(carta, actual, oponente, eventos):
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
def aplicar_carta(carta, actual, oponente, eventos):
    for code in carta.nomenclatura.split('+'):
        fn = HANDLERS.get(code.strip().upper())
        if fn:
            fn(carta, actual, oponente, eventos)
