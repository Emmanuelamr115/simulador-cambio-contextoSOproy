"""Interfaz del simulador de cambio de contexto."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from planificador import Simulador


class Ventana:
    NEGRO = "#000000"
    PANEL = "#0a0d0c"
    BORDE = "#26332d"
    TEXTO = "#e5eee8"
    SUAVE = "#93a99c"
    VERDE = "#43f59b"
    ROJO = "#ff6375"

    PALETA = [
        ("Azul", "#70b7ff"),
        ("Verde", "#43f59b"),
        ("Amarillo", "#f5d76e"),
        ("Violeta", "#b39aff"),
        ("Rosa", "#ff94c7"),
        ("Cian", "#65e3ed"),
        ("Naranja", "#ffad65"),
        ("Lima", "#b9ed69"),
        ("Lavanda", "#c7baff"),
        ("Coral", "#ff9387"),
        ("Acero", "#a1bfd3"),
        ("Menta", "#94e3b8"),
        ("Crema", "#eee2a8"),
        ("Malva", "#d7a9d8"),
        ("Salmón", "#eeb4b4"),
        ("Turquesa", "#72cebc"),
        ("Durazno", "#e7c4a1"),
        ("Oliva", "#c7d695"),
        ("Lila", "#e2a4ed"),
        ("Celeste", "#a5dfef"),
    ]

    def __init__(self, root):
        self.root = root
        self.tarea = None

        root.title("CTX / Miniproyecto 1 · Cambio de contexto")
        root.configure(bg=self.NEGRO)

        ancho = min(1280, root.winfo_screenwidth() - 60)
        alto = min(920, root.winfo_screenheight() - 90)
        root.geometry(f"{ancho}x{alto}")
        root.minsize(820, 650)

        self.estilos()

        base = tk.Frame(
            root,
            bg=self.NEGRO,
            padx=16,
            pady=12,
        )
        base.pack(fill="both", expand=True)
        base.columnconfigure(0, weight=1)

        # El registro recibe el espacio vertical sobrante.
        base.rowconfigure(9, weight=1)

        # Encabezado.
        cabecera = tk.Frame(base, bg=self.NEGRO)
        cabecera.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 10),
        )

        self.texto(
            cabecera, "CTX /", 27, self.VERDE, True
        ).pack(side="left")

        titulos = tk.Frame(cabecera, bg=self.NEGRO)
        titulos.pack(side="left", padx=16)

        self.texto(
            titulos,
            "CAMBIO DE CONTEXTO",
            16,
            negrita=True,
        ).pack(anchor="w")

        self.texto(
            titulos,
            "ROUND ROBIN   /   UNA CPU   /   CONTEXTO POR PROCESO",
            9,
            self.SUAVE,
        ).pack(anchor="w")

        self.indicador = self.texto(
            cabecera,
            "● PREPARADO",
            11,
            self.VERDE,
            True,
        )
        self.indicador.pack(side="right")

        # Configuración.
        config = self.panel(base, 1, "01 / CONFIGURACIÓN")

        self.texto(
            config, "RÁFAGAS", 9, self.SUAVE
        ).pack(side="left")

        self.rafagas = tk.StringVar(value="5, 3, 4")
        self.quantum = tk.StringVar(value="2")

        self.entrada(
            config, self.rafagas, 22
        ).pack(side="left", padx=(8, 18))

        self.texto(
            config, "QUANTUM", 9, self.SUAVE
        ).pack(side="left")

        self.entrada(
            config, self.quantum, 5
        ).pack(side="left", padx=8)

        self.boton(
            config,
            "↺ APLICAR / REINICIAR",
            self.reiniciar,
            rojo=True,
        ).pack(side="left", padx=8)

        # Controles.
        controles = tk.Frame(base, bg=self.NEGRO)
        controles.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=9,
        )

        self.paso_btn = self.boton(
            controles,
            "▷ UN PASO",
            self.paso,
        )
        self.paso_btn.pack(side="left")

        self.auto_btn = self.boton(
            controles,
            "▶ AUTOMÁTICO",
            self.iniciar,
            fuerte=True,
        )
        self.auto_btn.pack(side="left", padx=7)

        self.pausa_btn = self.boton(
            controles,
            "Ⅱ PAUSAR",
            self.pausar,
            rojo=True,
        )
        self.pausa_btn.pack(side="left")

        self.boton(
            controles,
            "↓ EXPORTAR",
            self.exportar,
        ).pack(side="left", padx=7)

        self.texto(
            controles, "RÁPIDO", 8, self.SUAVE
        ).pack(side="left", padx=(10, 3))

        self.velocidad = tk.DoubleVar(value=650)

        ttk.Scale(
            controles,
            from_=100,
            to=1500,
            variable=self.velocidad,
        ).pack(side="left", fill="x", expand=True)

        self.texto(
            controles, "LENTO", 8, self.SUAVE
        ).pack(side="left", padx=3)

        # Indicadores de CPU.
        tarjetas = tk.Frame(base, bg=self.NEGRO)
        tarjetas.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 7),
        )

        self.valores = {}

        nombres = (
            "CPU",
            "PC / ACC",
            "RELOJ",
            "PRÓXIMA FASE",
        )

        for indice, nombre in enumerate(nombres):
            tarjetas.columnconfigure(
                indice,
                weight=1,
                uniform="tarjetas",
            )

            caja = tk.Frame(
                tarjetas,
                bg=self.PANEL,
                highlightbackground=self.BORDE,
                highlightthickness=1,
                padx=10,
                pady=7,
            )
            caja.grid(
                row=0,
                column=indice,
                sticky="nsew",
                padx=(0 if indice == 0 else 6, 0),
            )

            self.texto(
                caja, nombre, 9, self.SUAVE
            ).pack(anchor="w")

            valor = self.texto(
                caja, "—", 13, self.VERDE, True
            )
            valor.pack(anchor="w", pady=(3, 0))
            self.valores[nombre] = valor

        self.cola = self.texto(
            base, "", 10, self.SUAVE
        )
        self.cola.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )

        # Tabla compacta de procesos.
        tabla_area = self.panel(
            base,
            5,
            "02 / PROCESOS · CONTEXTO GUARDADO EN EL PCB",
        )
        tabla_area.columnconfigure(0, weight=1)

        columnas = (
            "Proceso",
            "Estado",
            "Ráfaga",
            "Restante",
            "PC guardado",
            "ACC guardado",
            "Espera",
            "Fin / retorno",
        )

        self.tabla = ttk.Treeview(
            tabla_area,
            columns=columnas,
            show="headings",
            height=3,
            selectmode="none",
        )

        for columna in columnas:
            self.tabla.heading(columna, text=columna)
            self.tabla.column(
                columna,
                width=130 if columna == "Estado" else 110,
                minwidth=95,
                anchor="center",
            )

        self.tabla.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        scroll_y = ttk.Scrollbar(
            tabla_area,
            orient="vertical",
            command=self.tabla.yview,
        )
        scroll_y.grid(row=0, column=1, sticky="ns")

        scroll_x = ttk.Scrollbar(
            tabla_area,
            orient="horizontal",
            command=self.tabla.xview,
        )
        scroll_x.grid(row=1, column=0, sticky="ew")

        self.tabla.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )

        # Colores de estado con mayor contraste.
        estados = [
            ("LISTO", "#123c68", "#9dd2ff"),
            ("EJECUTANDO", "#075c35", "#79ffb5"),
            ("TERMINADO", "#343a40", "#e1e5e9"),
        ]

        for estado, fondo, letra in estados:
            self.tabla.tag_configure(
                estado,
                background=fondo,
                foreground=letra,
                font=("Arial", 10, "bold"),
            )

        # Leyenda con los mismos colores de la tabla.
        leyenda_estados = tk.Frame(
            tabla_area,
            bg=self.PANEL,
        )
        leyenda_estados.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(9, 2),
        )

        self.texto(
            leyenda_estados,
            "ESTADOS",
            9,
            self.SUAVE,
            True,
        ).pack(side="left", padx=(0, 12))

        etiquetas = [
            ("● AZUL · LISTO", "#123c68", "#9dd2ff"),
            ("● VERDE · EJECUTANDO", "#075c35", "#79ffb5"),
            ("● GRIS · TERMINADO", "#343a40", "#e1e5e9"),
        ]

        for texto, fondo, letra in etiquetas:
            tk.Label(
                leyenda_estados,
                text=texto,
                bg=fondo,
                fg=letra,
                font=("Arial", 10, "bold"),
                padx=12,
                pady=6,
                highlightthickness=1,
                highlightbackground=letra,
            ).pack(side="left", padx=(0, 10))

        # Línea de tiempo.
        linea = self.panel(
            base,
            6,
            "03 / LÍNEA DE TIEMPO · UN BLOQUE = UN CICLO",
        )
        linea.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            linea,
            bg=self.NEGRO,
            height=65,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="ew")

        scroll = ttk.Scrollbar(
            linea,
            orient="horizontal",
            command=self.canvas.xview,
        )
        scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=scroll.set)

        # Leyenda de colores por proceso.
        self.leyenda = tk.Canvas(
            linea,
            bg=self.PANEL,
            height=30,
            highlightthickness=0,
        )
        self.leyenda.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(3, 0),
        )

        scroll_leyenda = ttk.Scrollbar(
            linea,
            orient="horizontal",
            command=self.leyenda.xview,
        )
        scroll_leyenda.grid(
            row=3,
            column=0,
            sticky="ew",
        )

        self.leyenda.configure(
            xscrollcommand=scroll_leyenda.set,
        )

        # Resultados.
        self.resumen = self.texto(
            base, "", 10, self.VERDE, True
        )
        self.resumen.grid(
            row=7,
            column=0,
            sticky="ew",
            pady=7,
        )

        self.texto(
            base,
            "04 / REGISTRO DE CONTEXTO",
            10,
            self.SUAVE,
            True,
        ).grid(
            row=8,
            column=0,
            sticky="w",
            pady=(0, 5),
        )

        # Registro visible, sin pestañas.
        self.log = ScrolledText(
            base,
            height=5,
            bg="#050806",
            fg="#d1e0d7",
            insertbackground=self.VERDE,
            font=("Courier", 10),
            wrap="word",
            state="disabled",
            relief="flat",
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground=self.BORDE,
        )
        self.log.grid(
            row=9,
            column=0,
            sticky="nsew",
        )

        self.log.tag_configure(
            "restaurar",
            foreground="#79bdff",
        )
        self.log.tag_configure(
            "guardar",
            foreground="#f0ce79",
        )
        self.log.tag_configure(
            "terminar",
            foreground=self.VERDE,
        )

        self.log.vbar.configure(
            bg=self.PANEL,
            troughcolor=self.NEGRO,
            activebackground="#365344",
        )

        self.texto(
            base,
            "PC: siguiente instrucción · ACC: acumulador · "
            "Colores de la línea: identidad del proceso, no su estado.",
            9,
            self.SUAVE,
        ).grid(
            row=10,
            column=0,
            sticky="w",
            pady=(7, 0),
        )

        base.bind(
            "<Configure>",
            lambda evento: self.ajustar_textos(evento.width),
        )

        root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.reiniciar()

    def texto(
        self,
        padre,
        contenido,
        tam=10,
        color=None,
        negrita=False,
    ):
        return tk.Label(
            padre,
            text=contenido,
            bg=padre.cget("bg"),
            fg=color or self.TEXTO,
            font=(
                "Arial",
                tam,
                "bold" if negrita else "normal",
            ),
            anchor="w",
            justify="left",
        )

    def panel(self, padre, fila, titulo):
        marco = tk.Frame(
            padre,
            bg=self.PANEL,
            highlightbackground=self.BORDE,
            highlightthickness=1,
            padx=10,
            pady=7,
        )
        marco.grid(
            row=fila,
            column=0,
            sticky="ew",
            pady=(0, 6),
        )

        self.texto(
            marco, titulo, 9, self.SUAVE, True
        ).pack(anchor="w", pady=(0, 7))

        interior = tk.Frame(marco, bg=self.PANEL)
        interior.pack(fill="both", expand=True)

        return interior

    def entrada(self, padre, variable, ancho):
        return tk.Entry(
            padre,
            textvariable=variable,
            width=ancho,
            bg=self.NEGRO,
            fg=self.VERDE,
            insertbackground=self.VERDE,
            selectbackground="#1d583a",
            selectforeground="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.BORDE,
            highlightcolor=self.VERDE,
            font=("Courier", 12),
        )

    def boton(
        self,
        padre,
        texto,
        comando,
        rojo=False,
        fuerte=False,
    ):
        color = self.ROJO if rojo else self.VERDE

        if fuerte:
            fondo = color
        else:
            fondo = "#281014" if rojo else "#0c2418"

        return tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=fondo,
            fg=self.NEGRO if fuerte else color,
            activebackground=color,
            activeforeground=self.NEGRO,
            disabledforeground="#668073",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            highlightthickness=1,
            highlightbackground=color,
            highlightcolor=color,
        )

    def estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background=self.PANEL,
            fieldbackground=self.PANEL,
            foreground=self.TEXTO,
            rowheight=27,
            borderwidth=0,
            font=("Arial", 10),
        )

        estilo.configure(
            "Treeview.Heading",
            background="#16221c",
            foreground="#c7ded0",
            relief="flat",
            font=("Arial", 10, "bold"),
        )
        estilo.map(
            "Treeview.Heading",
            background=[("active", "#22372b")],
        )

        estilo.configure(
            "TScrollbar",
            background="#263d30",
            troughcolor=self.NEGRO,
            arrowcolor=self.VERDE,
            bordercolor=self.NEGRO,
            lightcolor="#263d30",
            darkcolor="#263d30",
        )
        estilo.map(
            "TScrollbar",
            background=[("active", "#3c624b")],
        )

        estilo.configure(
            "Horizontal.TScale",
            background=self.VERDE,
            troughcolor="#17251d",
            bordercolor=self.NEGRO,
            lightcolor=self.VERDE,
            darkcolor=self.VERDE,
        )

    def ajustar_textos(self, ancho):
        for etiqueta in (self.cola, self.resumen):
            etiqueta.configure(
                wraplength=max(300, ancho - 35)
            )

    def actualizar_leyenda(self):
        self.leyenda.delete("all")
        x = 8

        for proceso in self.sim.procesos:
            nombre, color = self.PALETA[proceso.pid - 1]

            self.leyenda.create_rectangle(
                x,
                9,
                x + 12,
                21,
                fill=color,
                outline="",
            )

            item = self.leyenda.create_text(
                x + 19,
                15,
                text=f"P{proceso.pid} / {nombre}",
                fill=self.TEXTO,
                anchor="w",
                font=("Arial", 10),
            )

            x = self.leyenda.bbox(item)[2] + 24

        self.leyenda.configure(
            scrollregion=(0, 0, x, 30)
        )
        self.leyenda.xview_moveto(0)

    def reiniciar(self):
        try:
            rafagas = [
                int(valor.strip())
                for valor in self.rafagas.get().split(",")
            ]
            quantum = int(self.quantum.get())

            if len(rafagas) > 20 or sum(rafagas) > 2000:
                raise ValueError(
                    "Usa como máximo 20 procesos "
                    "y 2000 ciclos totales."
                )

            nuevo = Simulador(rafagas, quantum)

        except ValueError as error:
            messagebox.showerror(
                "Configuración inválida",
                str(error),
            )
            return

        self.pausar()
        self.sim = nuevo

        self.tabla.configure(
            height=min(5, max(3, len(nuevo.procesos)))
        )

        self.actualizar_leyenda()

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        self.canvas.xview_moveto(0)

        self.indicador.configure(
            text="● PREPARADO",
            fg=self.VERDE,
        )
        self.actualizar()

    def paso(self):
        if not self.sim.terminado:
            mensaje = self.sim.paso()

            if "→ TERMINADO" in mensaje:
                tag = "terminar"
            elif "Guardando" in mensaje:
                tag = "guardar"
            elif "Restaurando" in mensaje:
                tag = "restaurar"
            else:
                tag = ""

            self.log.configure(state="normal")
            self.log.insert(
                "end",
                mensaje + "\n",
                (tag,) if tag else (),
            )
            self.log.see("end")
            self.log.configure(state="disabled")

        self.actualizar()

    def iniciar(self):
        if self.tarea is None and not self.sim.terminado:
            self.paso_btn.configure(state="disabled")
            self.auto_btn.configure(state="disabled")

            self.indicador.configure(
                text="● AUTOMÁTICO",
                fg=self.VERDE,
            )
            self.tick()

    def tick(self):
        self.tarea = None
        self.paso()

        if not self.sim.terminado:
            self.tarea = self.root.after(
                int(self.velocidad.get()),
                self.tick,
            )
        else:
            self.pausar()

    def pausar(self):
        if self.tarea is not None:
            self.root.after_cancel(self.tarea)
            self.tarea = None

        self.paso_btn.configure(state="normal")
        self.auto_btn.configure(state="normal")

        if hasattr(self, "sim"):
            self.indicador.configure(
                text=(
                    "● FINALIZADO"
                    if self.sim.terminado
                    else "Ⅱ PAUSADO / MANUAL"
                ),
                fg=(
                    self.VERDE
                    if self.sim.terminado
                    else self.ROJO
                ),
            )

    def actualizar(self):
        s = self.sim

        self.valores["CPU"].configure(
            text=f"P{s.actual.pid}" if s.actual else "LIBRE"
        )
        self.valores["PC / ACC"].configure(
            text=f"{s.pc_cpu} / {s.acc_cpu}"
        )
        self.valores["RELOJ"].configure(
            text=f"{s.tiempo:03d} ciclos"
        )
        self.valores["PRÓXIMA FASE"].configure(
            text="FINALIZADO" if s.terminado else s.fase
        )

        cola = " → ".join(
            f"P{proceso.pid}"
            for proceso in s.cola
        )
        self.cola.configure(
            text="COLA DE LISTOS  /  " + (cola or "vacía")
        )

        self.tabla.delete(*self.tabla.get_children())

        for fila in s.tabla():
            self.tabla.insert(
                "",
                "end",
                values=fila,
                tags=(fila[1],),
            )

        # Bloques con borde y franja del color de cada proceso.
        self.canvas.delete("all")

        for indice, pid in enumerate(s.traza):
            x = indice * 46 + 8
            color = self.PALETA[pid - 1][1]

            self.canvas.create_rectangle(
                x,
                7,
                x + 43,
                37,
                fill="#101813",
                outline=color,
            )
            self.canvas.create_rectangle(
                x,
                7,
                x + 43,
                10,
                fill=color,
                outline="",
            )
            self.canvas.create_text(
                x + 21,
                24,
                text=f"P{pid}",
                fill=color,
                font=("Arial", 10, "bold"),
            )
            self.canvas.create_text(
                x,
                51,
                text=str(indice),
                fill=self.SUAVE,
                anchor="w",
            )

        self.canvas.create_text(
            len(s.traza) * 46 + 8,
            51,
            text=str(s.tiempo),
            fill=self.SUAVE,
            anchor="w",
        )
        self.canvas.configure(
            scrollregion=(
                0,
                0,
                max(100, len(s.traza) * 46 + 50),
                65,
            )
        )

        texto = (
            f"CAMBIOS  {s.cambios}"
            f"     /     CICLOS  {s.tiempo}"
        )

        if s.terminado:
            cantidad = len(s.procesos)

            espera = sum(
                proceso.fin - proceso.rafaga
                for proceso in s.procesos
            ) / cantidad

            retorno = sum(
                proceso.fin
                for proceso in s.procesos
            ) / cantidad

            texto += (
                f"     /     ESPERA MEDIA  {espera:.2f}"
                f"     /     RETORNO MEDIO  {retorno:.2f}"
            )

            self.indicador.configure(
                text="● FINALIZADO",
                fg=self.VERDE,
            )

        self.resumen.configure(text=texto)

    def exportar(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Registro de texto", "*.txt")],
        )

        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as archivo:
                    rafagas = [
                        proceso.rafaga
                        for proceso in self.sim.procesos
                    ]

                    archivo.write(
                        f"Round Robin | quantum={self.sim.quantum}"
                        f" | ráfagas={rafagas}\n"
                    )
                    archivo.write(
                        "\n".join(self.sim.historial)
                    )
                    archivo.write(
                        "\n\n" + self.resumen.cget("text")
                    )

            except OSError as error:
                messagebox.showerror(
                    "No se pudo guardar",
                    str(error),
                )

    def cerrar(self):
        self.pausar()
        self.root.destroy()


def iniciar_interfaz():
    root = tk.Tk()
    Ventana(root)
    root.mainloop()