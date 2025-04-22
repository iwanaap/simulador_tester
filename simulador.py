# simulador.py
# -*- coding: utf-8 -*-

import random
import datetime
import pandas as pd
from datos_rulkanis import cartas_accion, distribucion_equipamiento, equipamiento_sets_nominales
from reglas import lanzar_dado, obtener_categoria, aplicar_dano, aplicar_carta

class Carta:
    def __init__(self, nombre, nomenclatura, nivel):
        self.nombre = nombre
        self.nomenclatura = nomenclatura
        self.nivel = nivel
        self.tipo = self.definir_tipo()

    def definir_tipo(self):
        uni = self.nombre.upper()
        if "AZAR" in uni:
            return "AZAR"
        elif "CERTERO" in uni:
            return "CERTERO"
        return "NORMAL"

    def accion_principal(self):
        return self.nomenclatura.split("+")[0].strip()

    def __repr__(self):
        return f"{self.nombre} (Nivel {self.nivel}, Tipo: {self.tipo})"

class Jugador:
    def __init__(self, nombre, mazo_cartas, origen_set):
        self.nombre = nombre
        self.mazo = list(mazo_cartas)
        random.shuffle(self.mazo)
        self.origen_set = origen_set
        self.mano = []
        self.vida = 15
        self.suerte_turnos = 0
        self.descartadas = []
        self.estado = {
            "defensa": 0,
            "sangrado": 0,
            "fuego": 0,
            "congelado": 0,
            "paralizado": 0,
            "esquiva": False
        }

    def robar(self, cantidad=1):
        for _ in range(cantidad):
            if self.mazo:
                self.mano.append(self.mazo.pop(0))

    def activar_suerte(self):
        self.suerte_turnos = 4

    def tiene_suerte(self):
        return self.suerte_turnos > 0

    def esta_vivo(self):
        return self.vida > 0

    def sin_cartas(self):
        return not self.mazo and not self.mano

    def actualizar_estados(self):
        if self.suerte_turnos > 0:
            self.suerte_turnos -= 1

    def __str__(self):
        return f"{self.nombre} (Vida: {self.vida}, Cartas en mazo: {len(self.mazo)})"

def construir_lista_cartas():
    return [Carta(c["nombre"], c["nomenclatura"], c["nivel"]) for c in cartas_accion]

def seleccionar_parte(parte, sets_disponibles):
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

        for nivel, cant in dist.items():
            cand = [c for c in disp if c.nivel == nivel and c not in usados]
            elegidos = cand[:cant]
            mazo.extend(elegidos)
            usados.extend(elegidos)

    # Ahora sí agregamos las 10 cartas extras
    print("\n--- Selección de 10 cartas adicionales ---")
    extras = {1:2, 2:2, 3:2, 4:2, 5:2}
    for nivel, cant in extras.items():
        mazo.extend(elegir_cartas_por_nivel(todas, nivel, cant))

    print(f"\nResumen del mazo de {nombre_jugador} (total {len(mazo)} cartas):")
    for c in mazo:
        print(" -", c)

    return mazo, origen


def aplicar_efectos_estado(jugador, estado):
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

def simular_varias_partidas(mazo1, origen1, mazo2, origen2, repeticiones):
    resumen = []
    detalle = []

    for partida in range(1, repeticiones+1):
        j1 = Jugador("Jugador 1", mazo1, origen1)
        j2 = Jugador("Jugador 2", mazo2, origen2)
        j1.robar(5)
        j2.robar(5)
        turno = 0
        actual, oponente = (j1, j2) if random.randint(1,10)>=5 else (j2, j1)

        while j1.esta_vivo() and j2.esta_vivo() and not j1.sin_cartas() and not j2.sin_cartas():
            turno += 1
            print(f"\nTurno {turno} - {actual.nombre}")
            eventos_ini, actual.estado, saltar = aplicar_efectos_estado(actual, actual.estado)
            for e in eventos_ini:
                print("  >", e)

            # — LOGEAR inicio de turno, incluso si salta —
            detalle.append({
                "Partida": partida,
                "Turno": turno,
                "Jugador": actual.nombre,
                "Fase": "InicioTurno",
                "Evento": "; ".join(eventos_ini) or "—",
                "SaltaTurno": saltar,
                "Vida J1": j1.vida,
                "Defensa J1": j1.estado["defensa"],
                "Vida J2": j2.vida,
                "Defensa J2": j2.estado["defensa"]
            })

            if saltar:
                print(f"{actual.nombre} pierde el turno")
                actual.actualizar_estados()
                actual.robar(1)
                actual, oponente = oponente, actual
                continue

            jugadas = []
            total_nivel = 0
            usadas_categorias = set()

            while len(jugadas) < 3:
                dispo = [
                    c for c in actual.mano
                    if total_nivel + c.nivel <= 10
                    and obtener_categoria(c) not in usadas_categorias
                ]
                if not dispo:
                    break

                carta = max(dispo, key=lambda c: c.nivel)
                categoria = obtener_categoria(carta)

                exito = True
                dado = "-"
                if carta.tipo == "AZAR":
                    d = lanzar_dado()
                    limite = 4 if actual.tiene_suerte() else 6
                    exito = d >= limite
                    dado = d

                resultado = "Éxito" if exito else "Fallo"
                evento = f"{carta.nombre} ({resultado}"
                if dado != "-":
                    evento += f", dado={dado}"
                evento += ")"

                if exito:
                    eventos_carta = []
                    aplicar_carta(carta, actual, oponente, eventos_carta)
                    if eventos_carta:
                        evento += " | " + " & ".join(eventos_carta)

                    total_nivel += carta.nivel
                    usadas_categorias.add(categoria)
                    jugadas.append(carta)

                    detalle.append({
                        "Partida": partida,
                        "Turno": turno,
                        "Jugador": actual.nombre,
                        "Carta": carta.nombre,
                        "Nivel": carta.nivel,
                        "Tipo": carta.tipo,
                        "Dado": dado,
                        "Resultado": resultado,
                        "Evento": evento,
                        "SaltaTurno": saltar,
                        "Vida J1": j1.vida,
                        "Defensa J1": j1.estado["defensa"],
                        "Vida J2": j2.vida,
                        "Defensa J2": j2.estado["defensa"]
                    })

                actual.mano.remove(carta)
                actual.descartadas.append(carta)

            actual.robar(1)
            actual.actualizar_estados()
            actual, oponente = oponente, actual

        if j1.vida > j2.vida:
            ganador = j1.nombre
        elif j2.vida > j1.vida:
            ganador = j2.nombre
        else:
            ganador = "Empate"

        resumen.append({
            "Partida": partida,
            "Ganador": ganador,
            "Vida Jugador 1": j1.vida,
            "Defensa J1": j1.estado["defensa"],   
            "Vida Jugador 2": j2.vida,
            "Defensa J2": j2.estado["defensa"]
        })

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
    rep = int(input("\n¿Cuántas simulaciones quieres?: "))
    simular_varias_partidas(mazo1, origen1, mazo2, origen2, rep)
