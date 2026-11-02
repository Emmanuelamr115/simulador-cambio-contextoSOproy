"""Interfaz gráfica Tkinter; utiliza el planificador sin duplicar su lógica."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from planificador import Simulador


class Ventana:
    def __init__(self, root):
        self.root = root
        self.tarea = None
        root.title('Simulador de cambio de contexto · Round Robin')
        root.geometry('1120x820')
        root.minsize(960, 680)
        root.configure(bg='#101827')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#101827')
        style.configure('TLabel', background='#101827', foreground='#e7edf5', font=('Arial', 11))
        style.configure('TButton', padding=7, font=('Arial', 10))
        style.configure('Treeview', rowheight=32, font=('Arial', 10))
        frame = ttk.Frame(root, padding=18)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='CAMBIO DE CONTEXTO', font=('Arial', 23, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Una CPU · Round Robin · Contexto guardado en el PCB de cada proceso').pack(anchor='w', pady=(3, 15))
        config = ttk.Frame(frame)
        config.pack(fill='x')
        self.rafagas = tk.StringVar(value='5, 3, 4')
        self.quantum = tk.StringVar(value='2')
        ttk.Label(config, text='Ráfagas:').pack(side='left')
        ttk.Entry(config, textvariable=self.rafagas, width=24).pack(side='left', padx=8)
        ttk.Label(config, text='Quantum:').pack(side='left')
        ttk.Entry(config, textvariable=self.quantum, width=5).pack(side='left', padx=8)
        ttk.Button(config, text='Aplicar / Reiniciar', command=self.reiniciar).pack(side='left')
        ttk.Label(frame, text='Ráfagas separadas por comas; todos llegan en t=0. Cambia los valores y pulsa Aplicar.').pack(anchor='w', pady=8)
        controls = ttk.Frame(frame)
        controls.pack(fill='x', pady=5)
        self.paso_btn = ttk.Button(controls, text='▶ Un paso', command=self.paso)
        self.paso_btn.pack(side='left')
        self.auto_btn = ttk.Button(controls, text='▶ Automático', command=self.iniciar)
        self.auto_btn.pack(side='left', padx=6)
        ttk.Button(controls, text='Ⅱ Pausar', command=self.pausar).pack(side='left')
        ttk.Button(controls, text='Exportar registro', command=self.exportar).pack(side='left', padx=6)
        ttk.Label(controls, text='Pausa visual (ms):').pack(side='left', padx=8)
        self.velocidad = tk.IntVar(value=650)
        ttk.Scale(controls, from_=100, to=1500, variable=self.velocidad).pack(side='left', fill='x', expand=True)
        self.cpu = ttk.Label(frame, font=('Arial', 13, 'bold'))
        self.cpu.pack(anchor='w', pady=(15, 5))
        self.cola = ttk.Label(frame)
        self.cola.pack(anchor='w', pady=5)
        columns = ('Proceso', 'Estado', 'Ráfaga', 'Restante', 'PC guardado', 'ACC guardado', 'Espera', 'Fin / retorno')
        self.tabla = ttk.Treeview(frame, columns=columns, show='headings', height=6)
        for c in columns:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=115, anchor='center')
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.tabla.pack(fill='x', pady=8)
        for estado, color in [('LISTO', '#dbeafe'), ('EJECUTANDO', '#bbf7d0'), ('TERMINADO', '#e2e8f0')]:
            self.tabla.tag_configure(estado, background=color, foreground='#111827')
        ttk.Label(frame, text='Azul: listo  •  Verde: ejecutando  •  Gris: terminado | PC = contador de programa; ACC = acumulador').pack(anchor='w')
        ttk.Label(frame, text='LÍNEA DE TIEMPO · cada bloque representa un ciclo de CPU').pack(anchor='w', pady=(13, 5))
        self.canvas = tk.Canvas(frame, height=65, bg='#1c293c', highlightthickness=0)
        self.canvas.pack(fill='x')
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=self.canvas.xview)
        horizontal.pack(fill='x')
        self.canvas.configure(xscrollcommand=horizontal.set)
        self.resumen = ttk.Label(frame)
        self.resumen.pack(anchor='w', pady=8)
        self.log = ScrolledText(frame, height=9, bg='#0a1020', fg='#c8e5ff', font=('Courier', 10), wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True)
        root.protocol('WM_DELETE_WINDOW', self.cerrar)
        self.reiniciar()

    def reiniciar(self):
        try:
            rafagas = [int(x.strip()) for x in self.rafagas.get().split(',')]
            quantum = int(self.quantum.get())
            if len(rafagas) > 20 or sum(rafagas) > 2000:
                raise ValueError('Usa como máximo 20 procesos y 2000 ciclos totales.')
            nuevo = Simulador(rafagas, quantum)
        except ValueError as e:
            messagebox.showerror('Configuración inválida', str(e))
            return
        self.pausar()
        self.sim = nuevo
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')
        self.canvas.xview_moveto(0)
        self.actualizar()

    def paso(self):
        if not self.sim.terminado:
            mensaje = self.sim.paso()
            self.log.configure(state='normal')
            self.log.insert('end', mensaje + '\n')
            self.log.see('end')
            self.log.configure(state='disabled')
        self.actualizar()

    def iniciar(self):
        if self.tarea is None and not self.sim.terminado:
            self.paso_btn.configure(state='disabled')
            self.auto_btn.configure(state='disabled')
            self.tick()

    def tick(self):
        self.tarea = None
        self.paso()
        if not self.sim.terminado:
            self.tarea = self.root.after(int(self.velocidad.get()), self.tick)
        else:
            self.pausar()

    def pausar(self):
        if self.tarea is not None:
            self.root.after_cancel(self.tarea)
            self.tarea = None
        self.paso_btn.configure(state='normal')
        self.auto_btn.configure(state='normal')

    def actualizar(self):
        s = self.sim
        nombre = f'P{s.actual.pid}' if s.actual else 'libre'
        self.cpu.configure(text=f'CPU: {nombre}    PC={s.pc_cpu}    ACC={s.acc_cpu}    Tiempo={s.tiempo}    Próxima fase: {s.fase if not s.terminado else "FINALIZADO"}')
        self.cola.configure(text='Cola de listos: ' + (' → '.join(f'P{p.pid}' for p in s.cola) or '(vacía)'))
        self.tabla.delete(*self.tabla.get_children())
        for fila in s.tabla():
            self.tabla.insert('', 'end', values=fila, tags=(fila[1],))
        self.canvas.delete('all')
        colores = ['#60a5fa', '#34d399', '#fbbf24', '#c084fc', '#fb7185']
        for i, pid in enumerate(s.traza):
            x = i * 44 + 5
            self.canvas.create_rectangle(x, 6, x+42, 38, fill=colores[(pid-1) % len(colores)], outline='')
            self.canvas.create_text(x+21, 22, text=f'P{pid}', fill='#101827')
            self.canvas.create_text(x, 51, text=str(i), fill='white', anchor='w')
        self.canvas.create_text(len(s.traza)*44+5, 51, text=str(s.tiempo), fill='white', anchor='w')
        self.canvas.configure(scrollregion=(0, 0, max(1000, len(s.traza)*44+45), 65))
        texto = f'Cambios entre procesos: {s.cambios} | Ciclos ejecutados: {s.tiempo}'
        if s.terminado:
            espera = sum(p.fin-p.rafaga for p in s.procesos)/len(s.procesos)
            retorno = sum(p.fin for p in s.procesos)/len(s.procesos)
            texto += f' | Finalizado · Espera media: {espera:.2f} · Retorno medio: {retorno:.2f}'
        self.resumen.configure(text=texto)

    def exportar(self):
        ruta = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Registro de texto', '*.txt')])
        if ruta:
            try:
                with open(ruta, 'w', encoding='utf-8') as f:
                    f.write(f'Round Robin | quantum={self.sim.quantum} | ráfagas={[p.rafaga for p in self.sim.procesos]}\n')
                    f.write('\n'.join(self.sim.historial))
                    f.write('\n\n' + self.resumen.cget('text'))
            except OSError as e:
                messagebox.showerror('No se pudo guardar', str(e))

    def cerrar(self):
        self.pausar()
        self.root.destroy()


def iniciar_interfaz():
    root = tk.Tk()
    Ventana(root)
    root.mainloop()
