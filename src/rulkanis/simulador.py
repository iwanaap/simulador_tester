# simulador.py
# -*- coding: utf-8 -*-

import random
import datetime
import pandas as pd
from rulkanis.datos_rulkanis import cartas_accion, distribucion_equipamiento, equipamiento_sets_nominales
from rulkanis.reglas import lanzar_dado, obtener_categoria, determinar_exito_carta, aplicar_carta
from rulkanis.carta import Carta
from rulkanis.jugador import Jugador


def construir_lista_cartas():
    """
    Construye una lista de objetos de tipo Carta a partir de una lista de diccionarios predefinida
    llamada 'cartas_accion'.

    Retorna:
        list: Una lista de objetos Carta, donde cada objeto se crea utilizando los valores de las
        claves 'nombre', 'nomenclatura' y 'nivel' de cada diccionario en 'cartas_accion'.
    """
    return [Carta(c["nombre"], c["nomenclatura"], c["nivel"]) for c in cartas_accion]


def seleccionar_parte(parte, sets_disponibles):
    """
    Permite al usuario seleccionar una parte específica de un conjunto disponible.

    Args:
        parte (str): El nombre de la parte que se desea seleccionar.
        sets_disponibles (dict): Un diccionario donde las claves son los nombres de los conjuntos
                                 y los valores son diccionarios que contienen las partes disponibles.

    Returns:
        tuple: Una tupla que contiene:
            - key (str): El nombre del conjunto seleccionado.
            - valor (varios): El valor asociado a la parte seleccionada dentro del conjunto.

    Raises:
        ValueError: Si la entrada del usuario no es un número válido o está fuera del rango.
    """
    print(f"\nSelecciona {parte.upper()}:")
    nombres = list(sets_disponibles.keys())
    for i, nombre in enumerate(nombres):
        print(f"  {i+1}. {nombre}")
    while True:
        try:
            sel = int(input("Número del set: ")) - 1
            if 0 <= sel < len(nombres):
                key = nombres[sel]
                return key, sets_disponibles[key][parte.upper()]
        except:
            print("Entrada inválida.")


def elegir_cartas_por_nivel(cartas_disponibles, nivel, cantidad):
    opciones = [c for c in cartas_disponibles if c.nivel == nivel]
    seleccion = []
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
    EQUIP_KEYS = {
        'ARMA': 'Armas',
        'PECHERA': 'Pechera',
        'CASCO': 'Casco',
        'BOTAS': 'Botas',
        'GUANTES': 'Guantes'
    }

    for parte in ["ARMA", "BOTAS", "CASCO", "PECHERA", "GUANTES"]:
        set_name, noms = seleccionar_parte(parte, equipamiento_sets_nominales)
        origen[parte] = set_name

        # Filtramos las cartas de ese set
        disp = [c for c in todas if c.nomenclatura in noms]
        usados = []

        # Obtenemos la distribución correcta usando la clave plural
        clave_dist = EQUIP_KEYS[parte]
        dist = distribucion_equipamiento.get(clave_dist, {})

        for nivel, cantidad in dist.items():
            cand = [c for c in disp if c.nivel == nivel and c not in usados]
            elegidos = cand[:cantidad]
            mazo.extend(elegidos)
            usados.extend(elegidos)

    # Ahora sí agregamos las 10 cartas extras
    print("\n--- Selección de 10 cartas adicionales ---")
    extras = {1:2, 2:2, 3:2, 4:2, 5:2}  # nivel: cantidad
    for nivel, cantidad in extras.items():
        mazo.extend(elegir_cartas_por_nivel(todas, nivel, cantidad))

    print(f"\nResumen del mazo de {nombre_jugador} (total {len(mazo)} cartas):")
    for c in mazo:
        print(" -", c)

    return mazo, origen


def aplicar_efectos_estado(jugador: Jugador, estado: dict):
    eventos = []
    saltar = False

    # Sangrado
    if estado.get("sangrado",0) > 0:
        jugador.vida -= 1
        estado["sangrado"] -= 1
        eventos.append("Sangrado: -1 vida")

    # Fuego
    if estado.get("fuego",0) > 0:
        if estado["defensa"] > 0:
            estado["defensa"] -= 1
            eventos.append("Fuego: -1 defensa")
        else:
            jugador.vida -= 1
            eventos.append("Fuego: -1 vida")
        estado["fuego"] -= 1

    # Congelar
    if estado.get("congelado",0) > 0:
        estado["congelado"] -= 1
        eventos.append("Congelado: pierde turno")
        saltar = True
    # Paralizar (siempre chequeamos, no es elif de congelado)
    if estado.get("paralizado", 0) > 0:
        # umbral cambia si tiene suerte activada
        limite = 4 if jugador.tiene_suerte() else 6
        d = lanzar_dado()
        if d < limite:
            eventos.append(f"Paralizado: dado {d} (<{limite}), pierde turno")
            saltar = True
        else:
            eventos.append(f"Paralizado: dado {d} (≥{limite}), puede jugar")
        estado["paralizado"] -= 1

    return eventos, estado, saltar


def simular_partida(
    partida: int,
    j1: Jugador,
    j2: Jugador,
    jugador_actual: Jugador,
    jugador_oponente: Jugador,
):
    resumen = []
    detalle = []

    turno = 0
    while j1.puede_continuar() and j2.puede_continuar():
        turno += 1
        print(f"\nTurno {turno} - {jugador_actual.nombre}")
        eventos_ini, jugador_actual.estado, saltar = aplicar_efectos_estado(
            jugador_actual, jugador_actual.estado
        )
        for evento in eventos_ini:
            print("  >", evento)

        # — LOGEAR inicio de turno, incluso si salta —
        detalle.append(
            {
                "Partida": partida,
                "Turno": turno,
                "Jugador": jugador_actual.nombre,
                "Fase": "InicioTurno",
                "Evento": "; ".join(eventos_ini) or "—",
                "SaltaTurno": saltar,
                "Vida J1": j1.vida,
                "Defensa J1": j1.estado["defensa"],
                "Vida J2": j2.vida,
                "Defensa J2": j2.estado["defensa"],
            }
        )

        if saltar:
            print(f"{jugador_actual.nombre} pierde el turno")
            jugador_actual.actualizar_estados()
            jugador_actual.robar(1)
            jugador_actual, jugador_oponente = jugador_oponente, jugador_actual
            continue

        # --- INICIO de jugadas ---
        cartas_jugadas: list = []
        nivel_total = 0
        categorias_jugadas = set()

        while len(cartas_jugadas) < 3:
            # 1) Filtrar mano por coste (nivel) y categoría
            cartas_disponibles = [
                carta for carta in jugador_actual.mano
                if nivel_total + carta.nivel <= 10
                and obtener_categoria(carta) not in categorias_jugadas
            ]
            if not cartas_disponibles:
                break

            # 2) Elegir carta de mayor nivel
            carta = max(cartas_disponibles, key=lambda carta: carta.nivel)
            categoria = obtener_categoria(carta)

            # 3) Resolver AZAR / CERTERO
            exito, evento, resultado, dado = determinar_exito_carta(carta, jugador_actual)

            if exito:
                # 4) REACCIÓN: Esquivar dañado antes de aplicar la carta
                if categoria in ("ataque", "sangrado", "fuego"):
                    carta_de_esquive = next(
                        (
                            carta
                            for carta in jugador_oponente.mano
                            if carta.accion_principal().upper() in ("EA", "EC")
                        ),
                        None,
                    )
                    if carta_de_esquive:
                        eventos_reaccion = []
                        aplicar_carta(
                            carta=carta_de_esquive,
                            jugador_actual=jugador_oponente,
                            jugador_oponente=jugador_actual,
                            eventos=eventos_reaccion,
                        )
                        jugador_oponente.mano.remove(carta_de_esquive)
                        jugador_oponente.descartadas.append(carta_de_esquive)
                        evento += f" | REACCIÓN: {jugador_oponente.nombre} juega {carta_de_esquive.nombre} → {eventos_reaccion[0]}"
                        detalle.append(
                            {
                                "Partida": partida,
                                "Turno": turno,
                                "Jugador": jugador_actual.nombre,
                                "Carta": carta.nombre, 
                                "Resultado": "Esquivado",
                                "Evento": evento,
                                "Vida J1": j1.vida,
                                "Defensa J1": j1.estado["defensa"],
                                "Vida J2": j2.vida,
                                "Defensa J2": j2.estado["defensa"],
                            }
                        )
                        # descartamos la carta atacante y saltamos resto
                        jugador_actual.mano.remove(carta)
                        jugador_actual.descartadas.append(carta)
                        continue

                # 5) Si no esquivó, aplicamos la carta normalmente
                eventos_carta = []
                aplicar_carta(carta, jugador_actual, jugador_oponente, eventos_carta)
                if eventos_carta:
                    evento += " | " + " & ".join(eventos_carta)

                nivel_total += carta.nivel
                categorias_jugadas.add(categoria)
                cartas_jugadas.append(carta)

                detalle.append(
                    {
                        "Partida": partida,
                        "Turno": turno,
                        "Jugador": jugador_actual.nombre,
                        "Carta": carta.nombre,
                        "Nivel": carta.nivel,
                        "Tipo": carta.tipo,
                        "Dado": dado,
                        "Resultado": resultado,
                        "Evento": evento,
                        "Vida J1": j1.vida,
                        "Defensa J1": j1.estado["defensa"],
                        "Vida J2": j2.vida,
                        "Defensa J2": j2.estado["defensa"],
                    }
                )

            # 6) Descartar siempre la carta atacante
            jugador_actual.mano.remove(carta)
            jugador_actual.descartadas.append(carta)
            # --- FIN de jugadas ---

        jugador_actual.robar(1)
        jugador_actual.actualizar_estados()
        jugador_actual, jugador_oponente = jugador_oponente, jugador_actual

    if j1.vida > j2.vida:
        ganador = j1.nombre
    elif j2.vida > j1.vida:
        ganador = j2.nombre
    else:
        ganador = "Empate"

    resumen.append(
        {
            "Partida": partida,
            "Ganador": ganador,
            "Vida Jugador 1": j1.vida,
            "Defensa J1": j1.estado["defensa"],
            "Vida Jugador 2": j2.vida,
            "Defensa J2": j2.estado["defensa"],
        }
    )

    return resumen, detalle


def simular_varias_partidas(mazo1, origen1, mazo2, origen2, repeticiones):
    resumen_total = []
    detalle_total = []

    for partida in range(1, repeticiones+1):
        j1 = Jugador("Jugador 1", mazo1, origen1)
        j2 = Jugador("Jugador 2", mazo2, origen2)
        j1.robar(5)
        j2.robar(5)
        
        actual, oponente = (j1, j2) if random.randint(1,10)>=5 else (j2, j1)

        resumen, detalle = simular_partida(partida, j1, j2, actual, oponente)

        resumen_total.extend(resumen)
        detalle_total.extend(detalle)

    df_res = pd.DataFrame(resumen)
    df_det = pd.DataFrame(detalle)
    conteo = df_res["Ganador"].value_counts()
    total = len(df_res)

    resumen_final = []
    for jugador, origen in [("Jugador 1", origen1), ("Jugador 2", origen2)]:
        vict = conteo.get(jugador, 0)
        resumen_final.append({
            "Jugador": jugador,
            "Victorias": vict,
            "Porcentaje": round(100 * vict / total, 2),
            "Partes seleccionadas": ", ".join(f"{p}: {origen[p]}" for p in origen),
            "Cartas del mazo": ", ".join(c.nombre for c in (mazo1 if jugador=="Jugador 1" else mazo2))
        })

    df_jug = pd.DataFrame(resumen_final)

    filename = "resultados_simulacion.xlsx"
    try:
        with pd.ExcelWriter(filename) as writer:
            df_jug.to_excel(writer, sheet_name="Resumen", index=False)
            df_det.to_excel(writer, sheet_name="Detalle", index=False)
        print(f"\nSimulación finalizada. Resultados en '{filename}'")
    except PermissionError:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fn2 = f"resultados_simulacion_{ts}.xlsx"
        with pd.ExcelWriter(fn2) as writer:
            df_jug.to_excel(writer, sheet_name="Resumen", index=False)
            df_det.to_excel(writer, sheet_name="Detalle", index=False)
        print(f"\nEl archivo estaba abierto. Guardé resultados en '{fn2}'")


if __name__ == "__main__":
    mazo1, origen1 = construir_mazo_combinado("Jugador 1")
    mazo2, origen2 = construir_mazo_combinado("Jugador 2")
    reps = int(input("\n¿Cuántas simulaciones quieres?: "))
    simular_varias_partidas(mazo1, origen1, mazo2, origen2, reps)
