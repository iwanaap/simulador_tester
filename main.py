# simulador.py
# -*- coding: utf-8 -*-
import time
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
    
    repeticiones = int(input("\n¿Cuántas simulaciones quieres?: "))

    ask_write = input("¿Guardar resultados en Excel? (S/N): ")
    write_excel = ask_write.strip().upper() == "S"

    start = time.perf_counter()
    simular_varias_partidas(mazo1, origen1, mazo2, origen2, repeticiones, write_excel)
    end = time.perf_counter()
    print(f"\nSimulación completada en {end - start:.2f} segundos.")