"""Simulador de cambio de contexto: punto de entrada del programa."""
import argparse
from planificador import Simulador
from consola import ejecutar_consola


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consola', action='store_true', help='Ejecutar sin ventana gráfica')
    parser.add_argument('--rafagas', default='5,3,4', help='Ráfagas para el modo consola')
    parser.add_argument('--quantum', type=int, default=2, help='Quantum para el modo consola')
    args = parser.parse_args()
    if args.consola:
        try:
            s = Simulador([int(x) for x in args.rafagas.split(',')], args.quantum)
        except ValueError as e:
            parser.error(str(e))
        ejecutar_consola(s)
    else:
        try:
            from gui import iniciar_interfaz
            iniciar_interfaz()
        except ImportError:
            parser.exit(1, 'Falta Tkinter. En Ubuntu: sudo apt install python3-tk\nTambién puedes usar --consola.\n')


if __name__ == '__main__':
    main()
