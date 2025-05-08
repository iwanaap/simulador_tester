# simulador.py
# -*- coding: utf-8 -*-

from rulkanis.simulador import simular_varias_partidas
from rulkanis.mazo import construir_mazo_combinado, construir_mazo_random


if __name__ == "__main__":
    eleccion_mazo = input("¿Quieres un mazo combinado o aleatorio? (C/A): ").strip().upper()
    if eleccion_mazo == "C":
        mazo1, origen1 = construir_mazo_combinado("Jugador 1")
        mazo2, origen2 = construir_mazo_combinado("Jugador 2")
    elif eleccion_mazo == "A":
        mazo1, origen1 = construir_mazo_random("Jugador 1")
        mazo2, origen2 = construir_mazo_random("Jugador 2")
    else:
        print("Opción inválida. Saliendo.")
        exit(1)
    rep = int(input("\n¿Cuántas simulaciones quieres?: "))
    simular_varias_partidas(mazo1, origen1, mazo2, origen2, rep)
