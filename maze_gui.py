import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from typing import Tuple, Dict, Optional
import random
import time
import heapq


COLS = 30
ROWS = 20
CELL_SIZE = 25 

COLOR_WALL = "#1E3A5F"      
COLOR_PATH = "#FFFFFF"      
COLOR_START = "#4CAF50"     
COLOR_END = "#F44336"       
COLOR_FRONTIER = "#AED6F1"  
COLOR_VISITED = "#D6EAF8"   
COLOR_FINAL_PATH = "#FFD700" 
GRID_LINE_COLOR = "#DDDDDD"


CHAR_WALL = "#"
CHAR_PATH = " "
CHAR_START = "S"
CHAR_END = "E"


class MazeEditorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Solucionador de Labirintos — BFS Animado")

        
        self.labirinto = [[CHAR_PATH for _ in range(COLS)] for _ in range(ROWS)]
        self.grid_cells = [[None for _ in range(COLS)] for _ in range(ROWS)]

        self.inicio_pos: Optional[Tuple[int,int]] = None
        self.fim_pos: Optional[Tuple[int,int]] = None

        
        self.fila: deque = deque()
        self.visitados: set = set()
        self.predecessores: Dict[Tuple[int,int], Tuple[int,int]] = {}
        self.job_after = None

        self.algorithm_name: str = "BFS"
        self.search_start_time: Optional[float] = None
        self.nodes_expanded: int = 0

        self.tool_var = tk.StringVar(value="wall")
        self.algorithm_var = tk.StringVar(value="BFS")

       
        self.controls = []
        self._build_ui()
        self.draw_grid_initial()


    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=8, pady=8, fill="both", expand=True)

        canvas_width = COLS * CELL_SIZE
        canvas_height = ROWS * CELL_SIZE
        self.canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=10)

        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

        
        tools_frame = ttk.Frame(main_frame)
        tools_frame.grid(row=0, column=1, sticky="nw", padx=(10,0))

        ttk.Label(tools_frame, text="Ferramenta:").pack(anchor="w")
        for text, val in [("Parede (#)", "wall"), ("Caminho ( )", "path"), ("Início (S)", "start"), ("Fim (E)", "end")]:
            rb = ttk.Radiobutton(tools_frame, text=text, variable=self.tool_var, value=val)
            rb.pack(anchor="w", pady=2)
            self.controls.append(rb)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=1, sticky="nw", padx=(10,0), pady=(10,0))

        # Algorithm selection dropdown
        ttk.Label(btn_frame, text="Algoritmo:").pack(anchor="w", pady=(4,0))
        algo_choices = ["BFS", "DFS", "Dijkstra", "A*"]
        self.algo_dropdown = ttk.Combobox(btn_frame, values=algo_choices, state="readonly", textvariable=self.algorithm_var)
        self.algo_dropdown.pack(fill="x", pady=2)

        self.btn_start_bfs = ttk.Button(btn_frame, text="Iniciar Busca", command=self.iniciar_busca)
        self.btn_start_bfs.pack(fill="x", pady=4)
        self.controls.append(self.btn_start_bfs)

        self.btn_reset_search = ttk.Button(btn_frame, text="Resetar Busca", command=self.resetar_busca)
        self.btn_reset_search.pack(fill="x", pady=4)
        self.controls.append(self.btn_reset_search)

        self.btn_clear = ttk.Button(btn_frame, text="Limpar Labirinto", command=self.limpar_labirinto)
        self.btn_clear.pack(fill="x", pady=4)
        self.controls.append(self.btn_clear)

        # Random maze generator
        self.btn_random = ttk.Button(btn_frame, text="Gerar Labirinto Aleatório", command=self.gerar_labirinto_aleatorio)
        self.btn_random.pack(fill="x", pady=4)
        self.controls.append(self.btn_random)

        # Stats area
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=3, column=1, sticky="nw", padx=(10,0), pady=(10,0))
        ttk.Label(stats_frame, text="Estatísticas:").pack(anchor="w")
        self.stats_text = tk.Text(stats_frame, width=30, height=6, wrap="word", state="disabled")
        self.stats_text.pack()

        legend_frame = ttk.Frame(main_frame)
        legend_frame.grid(row=2, column=1, sticky="nw", padx=(10,0), pady=(10,0))
        ttk.Label(legend_frame, text="Legenda:").pack(anchor="w")
        self._add_legend_item(legend_frame, "Parede", COLOR_WALL)
        self._add_legend_item(legend_frame, "Caminho", COLOR_PATH)
        self._add_legend_item(legend_frame, "Início", COLOR_START)
        self._add_legend_item(legend_frame, "Fim", COLOR_END)
        self._add_legend_item(legend_frame, "Fronteira", COLOR_FRONTIER)
        self._add_legend_item(legend_frame, "Visitado", COLOR_VISITED)
        self._add_legend_item(legend_frame, "Caminho Final", COLOR_FINAL_PATH)


    def _add_legend_item(self, parent, text, color):
        f = ttk.Frame(parent)
        f.pack(anchor="w", pady=2)
        c = tk.Canvas(f, width=18, height=14)
        c.create_rectangle(0,0,18,14, fill=color, outline="#000000")
        c.pack(side="left", padx=(0,6))
        ttk.Label(f, text=text).pack(side="left")


    def draw_grid_initial(self):
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLOR_PATH, outline=GRID_LINE_COLOR)
                self.grid_cells[r][c] = rect


   
    def canvas_coords_to_cell(self, x, y):
        col, row = x // CELL_SIZE, y // CELL_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            return int(row), int(col)
        return None

    def on_canvas_click(self, event):
        pos = self.canvas_coords_to_cell(event.x, event.y)
        if pos:
            self.editar_celula(*pos)

    def on_canvas_drag(self, event):
        pos = self.canvas_coords_to_cell(event.x, event.y)
        if pos:
            self.editar_celula(*pos)

    def editar_celula(self, row: int, col: int):
        tool = self.tool_var.get()

        if tool == "start":
            if self.inicio_pos:
                ir, ic = self.inicio_pos
                self.labirinto[ir][ic] = CHAR_PATH
                self._color_cell(ir, ic, COLOR_PATH)
            self.inicio_pos = (row, col)
            self.labirinto[row][col] = CHAR_START
            self._color_cell(row, col, COLOR_START)
            return

        if tool == "end":
            if self.fim_pos:
                fr, fc = self.fim_pos
                self.labirinto[fr][fc] = CHAR_PATH
                self._color_cell(fr, fc, COLOR_PATH)
            self.fim_pos = (row, col)
            self.labirinto[row][col] = CHAR_END
            self._color_cell(row, col, COLOR_END)
            return

        if tool == "wall":
            self.labirinto[row][col] = CHAR_WALL
            self._color_cell(row, col, COLOR_WALL)
            if self.inicio_pos == (row, col): self.inicio_pos = None
            if self.fim_pos == (row, col): self.fim_pos = None
            return

        if tool == "path":
            self.labirinto[row][col] = CHAR_PATH
            self._color_cell(row, col, COLOR_PATH)
            if self.inicio_pos == (row, col): self.inicio_pos = None
            if self.fim_pos == (row, col): self.fim_pos = None


    def _color_cell(self, r, c, color):
        self.canvas.itemconfig(self.grid_cells[r][c], fill=color)


    def iniciar_busca(self):
        if not self.inicio_pos or not self.fim_pos:
            messagebox.showerror("Erro", "Defina um ponto de Início (S) e um ponto de Fim (E).")
            return
        self._set_controls_state("disabled")
        self._clear_search_coloring()

        self.algorithm_name = self.algorithm_var.get()
        self.nodes_expanded = 0
        self.search_start_time = time.time()

        if self.algorithm_name == "BFS":
            self.fila = deque([self.inicio_pos])
            self.visitados = {self.inicio_pos}
            self.predecessores = {}
            self._color_cell(*self.inicio_pos, COLOR_VISITED)
        elif self.algorithm_name == "DFS":
            self.fila = [self.inicio_pos]  
            self.visitados = {self.inicio_pos}
            self.predecessores = {}
            self._color_cell(*self.inicio_pos, COLOR_VISITED)
        elif self.algorithm_name in ("Dijkstra", "A*"):
            self.distance = {self.inicio_pos: 0}
            self.predecessores = {}
           
            self.fila = []
            start_priority = 0 if self.algorithm_name == "Dijkstra" else self._manhattan(self.inicio_pos, self.fim_pos)
            heapq.heappush(self.fila, (start_priority, self.inicio_pos))
            self._color_cell(*self.inicio_pos, COLOR_VISITED)
        else:
            messagebox.showerror("Erro", f"Algoritmo desconhecido: {self.algorithm_name}")
            self._set_controls_state("normal")
            return

        self._schedule_next_step(60)


    def _schedule_next_step(self, delay=80):
        self.job_after = self.root.after(delay, self.processar_passo)


    def processar_passo(self):
        
        if self.algorithm_name == "BFS":
            self.processar_passo_bfs()
        elif self.algorithm_name == "DFS":
            self.processar_passo_dfs()
        elif self.algorithm_name == "Dijkstra":
            self.processar_passo_dijkstra()
        elif self.algorithm_name == "A*":
            self.processar_passo_astar()
        else:
            
            self._set_controls_state("normal")
            self.job_after = None


    def processar_passo_bfs(self):
        if not self.fila:
            messagebox.showinfo("Resultado", "Caminho não encontrado.")
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=False)
            return

        atual = self.fila.popleft()
        if atual not in (self.inicio_pos, self.fim_pos):
            self._color_cell(*atual, COLOR_VISITED)

        if atual == self.fim_pos:
            self.reconstruir_caminho(atual)
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=True)
            return

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = atual[0]+dr, atual[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if (nr, nc) not in self.visitados and self.labirinto[nr][nc] != CHAR_WALL:
                    self.visitados.add((nr, nc))
                    self.predecessores[(nr, nc)] = atual
                    self.fila.append((nr, nc))
                    self.nodes_expanded += 1
                    if (nr, nc) not in (self.inicio_pos, self.fim_pos):
                        self._color_cell(nr, nc, COLOR_FRONTIER)

        self._schedule_next_step()


    def processar_passo_dfs(self):
        if not self.fila:
            messagebox.showinfo("Resultado", "Caminho não encontrado.")
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=False)
            return

        atual = self.fila.pop()
        if atual not in (self.inicio_pos, self.fim_pos):
            self._color_cell(*atual, COLOR_VISITED)

        if atual == self.fim_pos:
            self.reconstruir_caminho(atual)
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=True)
            return

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = atual[0]+dr, atual[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if (nr, nc) not in self.visitados and self.labirinto[nr][nc] != CHAR_WALL:
                    self.visitados.add((nr, nc))
                    self.predecessores[(nr, nc)] = atual
                    self.fila.append((nr, nc))
                    self.nodes_expanded += 1
                    if (nr, nc) not in (self.inicio_pos, self.fim_pos):
                        self._color_cell(nr, nc, COLOR_FRONTIER)

        self._schedule_next_step()


    def processar_passo_dijkstra(self):
        if not self.fila:
            messagebox.showinfo("Resultado", "Caminho não encontrado.")
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=False)
            return

        dist, atual = heapq.heappop(self.fila)
        
        if self.distance.get(atual, float('inf')) < dist:
            self._schedule_next_step()
            return

        if atual not in (self.inicio_pos, self.fim_pos):
            self._color_cell(*atual, COLOR_VISITED)

        if atual == self.fim_pos:
            self.reconstruir_caminho(atual)
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=True)
            return

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = atual[0]+dr, atual[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.labirinto[nr][nc] != CHAR_WALL:
                nd = self.distance.get(atual, float('inf')) + 1
                if nd < self.distance.get((nr, nc), float('inf')):
                    self.distance[(nr, nc)] = nd
                    self.predecessores[(nr, nc)] = atual
                    heapq.heappush(self.fila, (nd, (nr, nc)))
                    self.nodes_expanded += 1
                    if (nr, nc) not in (self.inicio_pos, self.fim_pos):
                        self._color_cell(nr, nc, COLOR_FRONTIER)

        self._schedule_next_step()


    def processar_passo_astar(self):
        if not self.fila:
            messagebox.showinfo("Resultado", "Caminho não encontrado.")
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=False)
            return

        fval, atual = heapq.heappop(self.fila)
        
        if atual in self.distance and fval - self._manhattan(atual, self.fim_pos) > self.distance.get(atual, float('inf')):
            self._schedule_next_step()
            return

        if atual not in (self.inicio_pos, self.fim_pos):
            self._color_cell(*atual, COLOR_VISITED)

        if atual == self.fim_pos:
            self.reconstruir_caminho(atual)
            self._set_controls_state("normal")
            self.job_after = None
            self._update_stats(found=True)
            return

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = atual[0]+dr, atual[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.labirinto[nr][nc] != CHAR_WALL:
                tentative_g = self.distance.get(atual, float('inf')) + 1
                if tentative_g < self.distance.get((nr, nc), float('inf')):
                    self.distance[(nr, nc)] = tentative_g
                    self.predecessores[(nr, nc)] = atual
                    fscore = tentative_g + self._manhattan((nr, nc), self.fim_pos)
                    heapq.heappush(self.fila, (fscore, (nr, nc)))
                    self.nodes_expanded += 1
                    if (nr, nc) not in (self.inicio_pos, self.fim_pos):
                        self._color_cell(nr, nc, COLOR_FRONTIER)

        self._schedule_next_step()


    def reconstruir_caminho(self, end_pos: Tuple[int,int]):
        path = []
        cur = end_pos
        while cur != self.inicio_pos:
            path.append(cur)
            cur = self.predecessores.get(cur)
            if cur is None: break
        for cell in reversed(path):
            if cell not in (self.inicio_pos, self.fim_pos):
                self._color_cell(*cell, COLOR_FINAL_PATH)
        # Update stats with the reconstructed path
        self._update_stats(found=True, path=path)
        messagebox.showinfo("Resultado", "Caminho encontrado!")


    
    def resetar_busca(self):
        if self.job_after:
            self.root.after_cancel(self.job_after)
            self.job_after = None
        self._clear_search_coloring()
        self.fila.clear()
        self.visitados.clear()
        self.predecessores.clear()
        self._set_controls_state("normal")

    def limpar_labirinto(self):
        if self.job_after:
            self.root.after_cancel(self.job_after)
            self.job_after = None

        for r in range(ROWS):
            for c in range(COLS):
                self.labirinto[r][c] = CHAR_PATH
                self._color_cell(r, c, COLOR_PATH)

        self.inicio_pos = None
        self.fim_pos = None
        self.fila.clear()
        self.visitados.clear()
        self.predecessores.clear()
        self._set_controls_state("normal")


    def gerar_labirinto_aleatorio(self, wall_prob: float = 0.28):
        # Fill maze randomly with walls, keep start/end clear
        for r in range(ROWS):
            for c in range(COLS):
                if random.random() < wall_prob:
                    self.labirinto[r][c] = CHAR_WALL
                    self._color_cell(r, c, COLOR_WALL)
                else:
                    self.labirinto[r][c] = CHAR_PATH
                    self._color_cell(r, c, COLOR_PATH)

        # Place start/end if not set or if they landed on wall
        if not self.inicio_pos or self.labirinto[self.inicio_pos[0]][self.inicio_pos[1]] == CHAR_WALL:
            self.inicio_pos = (0, 0)
            self.labirinto[0][0] = CHAR_START
            self._color_cell(0, 0, COLOR_START)
        else:
            r, c = self.inicio_pos
            self.labirinto[r][c] = CHAR_START
            self._color_cell(r, c, COLOR_START)

        if not self.fim_pos or self.labirinto[self.fim_pos[0]][self.fim_pos[1]] == CHAR_WALL:
            fr, fc = ROWS-1, COLS-1
            self.fim_pos = (fr, fc)
            self.labirinto[fr][fc] = CHAR_END
            self._color_cell(fr, fc, COLOR_END)
        else:
            r, c = self.fim_pos
            self.labirinto[r][c] = CHAR_END
            self._color_cell(r, c, COLOR_END)


    def _manhattan(self, a: Tuple[int,int], b: Tuple[int,int]) -> int:
        return abs(a[0]-b[0]) + abs(a[1]-b[1])


    def _update_stats(self, found: bool, path: Optional[list] = None):
        elapsed = None
        if self.search_start_time:
            elapsed = time.time() - self.search_start_time
        path_len = len(path) if path else (0 if not found else 0)
        nodes = getattr(self, 'nodes_expanded', 0)
        text = []
        text.append(f"Algoritmo: {self.algorithm_name}")
        text.append(f"Encontrado: {'Sim' if found else 'Não'}")
        text.append(f"Nós explorados: {nodes}")
        text.append(f"Comprimento do caminho: {path_len}")
        if elapsed is not None:
            text.append(f"Tempo (s): {elapsed:.3f}")

        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0', '\n'.join(text))
        self.stats_text.config(state='disabled')

    def _clear_search_coloring(self):
        for r in range(ROWS):
            for c in range(COLS):
                ch = self.labirinto[r][c]
                color = {
                    CHAR_WALL: COLOR_WALL,
                    CHAR_START: COLOR_START,
                    CHAR_END: COLOR_END,
                    CHAR_PATH: COLOR_PATH
                }[ch]
                self._color_cell(r, c, color)

    def _set_controls_state(self, state):
        for w in self.controls:
            w.config(state=state)
