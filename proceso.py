"""Modelo de proceso y su contexto guardado (PCB simplificado)."""
from dataclasses import dataclass


@dataclass
class Proceso:
    pid: int
    rafaga: int
    estado: str = 'LISTO'
    pc: int = 0
    acumulador: int = 0
    fin: object = None
    respuesta: object = None

