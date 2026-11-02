"""Planificador Round Robin y simulación del cambio de contexto."""
from collections import deque
from proceso import Proceso


class Simulador:
    """Cada paso es un despacho, un ciclo de CPU o un guardado de contexto."""
    def __init__(self, rafagas=(5, 3, 4), quantum=2):
        rafagas = list(rafagas)
        if type(quantum) is not int or quantum <= 0:
            raise ValueError('El quantum debe ser un entero positivo.')
        if not rafagas or any(type(n) is not int or n <= 0 for n in rafagas):
            raise ValueError('Introduce al menos una ráfaga entera positiva.')
        self.procesos = [Proceso(i + 1, n) for i, n in enumerate(rafagas)]
        self.cola = deque(self.procesos)
        self.quantum = quantum
        self.actual = None
        self.pc_cpu = self.acc_cpu = self.usado = self.tiempo = 0
        self.anterior = None
        self.cambios = 0
        self.fase = 'DESPACHAR'
        self.historial = []
        self.traza = []

    @property
    def terminado(self):
        return not self.cola and self.actual is None

    def paso(self):
        if self.terminado:
            return 'Simulación terminada.'
        if self.fase == 'DESPACHAR':
            p = self.cola.popleft()
            if self.anterior is not None and self.anterior != p.pid:
                self.cambios += 1
            self.actual = p
            self.pc_cpu, self.acc_cpu = p.pc, p.acumulador
            self.usado = 0
            p.estado = 'EJECUTANDO'
            if p.respuesta is None:
                p.respuesta = self.tiempo
            self.fase = 'EJECUTAR'
            mensaje = f'Restaurando contexto de P{p.pid}: PC={p.pc}, ACC={p.acumulador}. LISTO → EJECUTANDO.'
        elif self.fase == 'EJECUTAR':
            p = self.actual
            # Instrucción simulada: ACC += PID; PC apunta a la siguiente instrucción.
            self.acc_cpu += p.pid
            self.pc_cpu += 1
            self.usado += 1
            self.tiempo += 1
            self.traza.append(p.pid)
            mensaje = f'Proceso {p.pid} ejecutándose… PC CPU={self.pc_cpu}, ACC CPU={self.acc_cpu}; quantum {self.usado}/{self.quantum}.'
            if self.pc_cpu == p.rafaga or self.usado == self.quantum:
                self.fase = 'GUARDAR'
        else:
            p = self.actual
            p.pc, p.acumulador = self.pc_cpu, self.acc_cpu
            if p.pc == p.rafaga:
                p.estado = 'TERMINADO'
                p.fin = self.tiempo
                razon = 'Finalizó su ráfaga. EJECUTANDO → TERMINADO.'
            else:
                p.estado = 'LISTO'
                self.cola.append(p)
                razon = 'Quantum agotado. EJECUTANDO → LISTO; vuelve al final de la cola.'
            mensaje = f'Guardando estado de P{p.pid} en su PCB: PC={p.pc}, ACC={p.acumulador}. {razon}'
            self.anterior = p.pid
            self.actual = None
            self.pc_cpu = self.acc_cpu = 0
            self.fase = 'DESPACHAR'
        mensaje = f'[t={self.tiempo:03d}] {mensaje}'
        self.historial.append(mensaje)
        return mensaje

    def tabla(self):
        filas = []
        for p in self.procesos:
            ejecutado = self.pc_cpu if p is self.actual else p.pc
            espera = (p.fin if p.fin is not None else self.tiempo) - ejecutado
            filas.append((f'P{p.pid}', p.estado, p.rafaga, p.rafaga-ejecutado,
                          p.pc, p.acumulador, espera, p.fin if p.fin is not None else '—'))
        return filas

