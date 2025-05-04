# simulador.py
# -*- coding: utf-8 -*-

from rulkanis.simulador import construir_mazo_combinado, simular_varias_partidas


if __name__ == "__main__":
    mazo1, origen1 = construir_mazo_combinado("Jugador 1")
    mazo2, origen2 = construir_mazo_combinado("Jugador 2")
    rep = int(input("\n¿Cuántas simulaciones quieres?: "))
    simular_varias_partidas(mazo1, origen1, mazo2, origen2, rep)
