from .carta import Carta
from typing import Protocol

class JugadorProtocol(Protocol):
    nombre: str
    vida: int
    estado: dict
    mazo: list
    mano: list
    suerte_turnos: int
    descartadas: list
    salta_turno: bool

    def lanzar_dado(self) -> int:
        pass

    def aplicar_efectos_de_estado(self, evento):
        pass


class EventLogger:
    def __init__(self):
        self.events = []
    
    def log_event(self, event: str):
        self.events.append(event)

    def get_event_log(self, separator: str = " | "):
        return separator.join(self.events)
    
    def print_events(self):
        for event in self.events:
            print(event)


class Logger:
    def __init__(
        self,
        partida: int,
        turno: int,
        jugador: str,
        fase: str,
        j1: JugadorProtocol,
        j2: JugadorProtocol,
    ):
        self.partida = partida
        self.turno = turno
        self.jugador = jugador
        self.fase = fase
        self.j1 = j1
        self.j2 = j2
        self.evento: EventLogger = EventLogger()
        self.detalle: list = []


    def actualizar_campos(self, campos: dict):
        for key, value in campos.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"El campo '{key}' no existe en la clase Logger.")

    def log_inicio_turno(self, saltar: bool):
        
        self.detalle.append(
            {
                "Partida": self.partida,
                "Turno": self.turno,
                "Jugador": self.jugador,
                "Fase": "InicioTurno",
                "Evento": self.evento.get_event_log(separator="; ") or "—",
                "SaltaTurno": saltar,
                "Vida J1": self.j1.vida,
                "Defensa J1": self.j1.estado["defensa"],
                "Vida J2": self.j2.vida,
                "Defensa J2": self.j2.estado["defensa"]
            }
        )
        self.evento = EventLogger()  # Reiniciar el evento para el siguiente turno

    def log_reaccion(self, resultado: str, carta: Carta):
        self.detalle.append(
            {
                "Partida": self.partida,
                "Turno": self.turno,
                "Jugador": self.jugador,
                "Carta": carta.nombre,
                "Fase": "Reaccion",
                "Resultado": resultado,
                "Evento": self.evento.get_event_log(),
                "Vida J1": self.j1.vida,
                "Defensa J1": self.j1.estado["defensa"],
                "Vida J2": self.j2.vida,
                "Defensa J2": self.j2.estado["defensa"]
            }
        )
        self.evento = EventLogger()  # Reiniciar el evento para el siguiente turno

    def log_fin_jugada(self, carta: Carta, dado: int, resultado: str):
        
        self.detalle.append(
            {
                "Partida": self.partida,
                "Turno": self.turno,
                "Jugador": self.jugador,
                "Carta": carta.nombre,
                "Nivel": carta.nivel,
                "Tipo": carta.tipo,
                "Dado": dado,
                "Resultado": resultado,
                "Evento": " | " + self.evento.get_event_log(separator=" & "),
                "Vida J1": self.j1.vida,
                "Defensa J1": self.j1.estado["defensa"],
                "Vida J2": self.j2.vida,
                "Defensa J2": self.j2.estado["defensa"]
            }
        )
        self.evento = EventLogger()  # Reiniciar el evento para el siguiente turno
