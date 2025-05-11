# simulador.py
# -*- coding: utf-8 -*-

import random
import datetime
import pandas as pd
from rulkanis.datos_rulkanis import cartas_accion, distribucion_equipamiento, equipamiento_sets_nominales
from rulkanis.reglas import determinar_exito_carta, aplicar_carta
from rulkanis.carta import Carta
from rulkanis.jugador import Jugador
from rulkanis.logger import Logger, EventLogger
from rulkanis.mazo import construir_mazo_combinado


def fase_reaccion(
    carta_jugada: Carta,
    carta_de_esquive: Carta,
    jugador_actual: Jugador,
    jugador_oponente: Jugador,
    logger: Logger,
    evento: str,
):

    eventos_reaccion = []
    aplicar_carta(
        carta=carta_de_esquive,
        jugador_actual=jugador_oponente,
        jugador_oponente=jugador_actual,
        eventos=eventos_reaccion,
    )
    evento += f" | REACCIÓN: {jugador_oponente.nombre} juega {carta_de_esquive.nombre} → {eventos_reaccion[0]}"

    logger.actualizar_campos({'jugador': jugador_oponente.nombre})
    logger.log_reaccion(
        resultado="Esquivado" if jugador_oponente.estado["esquiva"] else "Fallido",
        carta=carta_de_esquive,
        evento=evento,
    )
    # oponente descarta la carta de esquive
    jugador_oponente.descartar(carta_de_esquive)
    # jugador activate descarta la carta atacante
    jugador_actual.descartar(carta_jugada)


def simular_partida(
    partida: int,
    j1: Jugador,
    j2: Jugador,
    jugador_actual: Jugador,
    jugador_oponente: Jugador,
):
    logger = Logger(
        partida=partida,
        turno=0,
        jugador=jugador_actual.nombre,
        fase="",
        evento="",
        j1=j1,
        j2=j2,
    )
    resumen = []

    turno = 0
    while j1.puede_continuar() and j2.puede_continuar():
        turno += 1
        print(f"\nTurno {turno} - {jugador_actual.nombre}")

        eventos_ini = jugador_actual.aplicar_efectos_de_estado()
        for evento in eventos_ini:
            print("  >", evento)

        logger.actualizar_campos(
            {
                "turno": turno,
                "jugador": jugador_actual.nombre,
                "fase": "InicioTurno",
                "evento": eventos_ini,
            }
        )

        # — LOGEAR inicio de turno, incluso si salta —
        logger.log_inicio_turno(saltar=jugador_actual.salta_turno)

        if jugador_actual.salta_turno:
            print(f"{jugador_actual.nombre} pierde el turno")
            jugador_actual.terminar_turno()
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
                and carta.categoria not in categorias_jugadas
            ]
            if not cartas_disponibles:
                break

            # 2) Elegir carta de mayor nivel
            carta = max(cartas_disponibles, key=lambda carta: carta.nivel)

            # 3) Resolver AZAR / CERTERO
            exito, evento, resultado, dado = determinar_exito_carta(carta, jugador_actual)

            if exito:
                if carta.categoria in ("ataque", "sangrado", "fuego"):
                    carta_de_esquive = next(
                        (
                            carta
                            for carta in jugador_oponente.mano
                            if carta.accion_principal().upper() in ("EA", "EC")
                        ),
                        None,
                    )
                    if carta_de_esquive:
                        fase_reaccion(
                            carta_jugada=carta,
                            carta_de_esquive=carta_de_esquive,
                            jugador_actual=jugador_actual,
                            jugador_oponente=jugador_oponente,
                            logger=logger,
                            evento=evento)
                        continue
                # # 4) REACCIÓN: Esquivar dañado antes de aplicar la carta                    

                # 5) Si no esquivó, aplicamos la carta normalmente
                eventos_carta = []
                aplicar_carta(carta, jugador_actual, jugador_oponente, eventos_carta)
                if eventos_carta:
                    evento += " | " + " & ".join(eventos_carta)

                nivel_total += carta.nivel
                categorias_jugadas.add(carta.categoria)
                cartas_jugadas.append(carta)

                logger.actualizar_campos({'jugador': jugador_actual.nombre})
                logger.log_fin_turno(
                    carta=carta,
                    dado=dado,
                    resultado=resultado,
                    evento=evento,
                )

            # 6) Descartar siempre la carta atacante
            jugador_actual.descartar(carta)
            # --- FIN de jugadas ---

        jugador_actual.terminar_turno()
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

    return resumen, logger.detalle


def simular_varias_partidas(mazo1, origen1, mazo2, origen2, repeticiones, write_excel=True):
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

    print(f'len(resumen_total) = {len(resumen_total)}')
    df_resumen = pd.DataFrame(resumen_total)
    df_detalle = pd.DataFrame(detalle_total)

    # print(df_det['partida'])
    conteo = df_resumen["Ganador"].value_counts()
    total = len(df_resumen)

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

    df_resumen_final = pd.DataFrame(resumen_final)

    if write_excel:
        print("\nGuardando resultados en Excel...")
        filename = "resultados_simulacion.xlsx"
        try:
            with pd.ExcelWriter(filename) as writer:
                df_resumen_final.to_excel(writer, sheet_name="Resumen", index=False)
                df_detalle.to_excel(writer, sheet_name="Detalle", index=False)
            print(f"\nSimulación finalizada. Resultados en '{filename}'")
        except PermissionError:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fn2 = f"resultados_simulacion_{ts}.xlsx"
            with pd.ExcelWriter(fn2) as writer:
                df_resumen_final.to_excel(writer, sheet_name="Resumen", index=False)
                df_detalle.to_excel(writer, sheet_name="Detalle", index=False)
            print(f"\nEl archivo estaba abierto. Guardé resultados en '{fn2}'")


if __name__ == "__main__":
    mazo1, origen1 = construir_mazo_combinado("Jugador 1")
    mazo2, origen2 = construir_mazo_combinado("Jugador 2")
    reps = int(input("\n¿Cuántas simulaciones quieres?: "))
    ask_write = input("¿Guardar resultados en Excel? (S/N): ")
    write_excel = ask_write.strip().upper() == "S"
    simular_varias_partidas(mazo1, origen1, mazo2, origen2, reps, write_excel)
