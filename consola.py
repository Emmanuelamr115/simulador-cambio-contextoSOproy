"""Presentación de la simulación en terminal, sin depender de Tkinter."""


def ejecutar_consola(s):
    while not s.terminado:
        print(s.paso())
        print('Estados: ' + ' | '.join(f'{p.pid}: {p.estado}' for p in s.procesos))
    print(f'Fin: {s.tiempo} ciclos; {s.cambios} cambios entre procesos.')
    print('Proceso / Estado / Ráfaga / Restante / PC / ACC / Espera / Retorno')
    for fila in s.tabla():
        print(' / '.join(map(str, fila)))
