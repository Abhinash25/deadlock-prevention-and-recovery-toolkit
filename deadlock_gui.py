#!/usr/bin/env python3
"""
Deadlock Prevention & Recovery Toolkit — Desktop GUI Edition
Run: python deadlock_gui.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Canvas
import random
import math
import threading
import time

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# ── Theme ──
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ORANGE = "#f97316"
ORANGE_HOVER = "#ea580c"
ORANGE_LIGHT = "#fff7ed"
GREEN = "#10b981"
GREEN_LIGHT = "#ecfdf5"
RED = "#ef4444"
RED_LIGHT = "#fef2f2"
BLUE = "#3b82f6"
BLUE_LIGHT = "#eff6ff"
STONE50 = "#fafaf9"
STONE100 = "#f5f5f4"
STONE200 = "#e7e5e3"
STONE400 = "#a8a29e"
STONE500 = "#78716c"
STONE600 = "#57534e"
STONE700 = "#44403c"
STONE800 = "#292524"
STONE900 = "#1c1917"
WHITE = "#ffffff"
AMBER = "#f59e0b"

FONT_FAMILY = "Segoe UI"

# ══════════════════════════════════════════
# ALGORITHMS
# ══════════════════════════════════════════

def bankers_safety_check(processes, resources, allocation, max_matrix, available):
    n, m = len(processes), len(resources)
    need = [[max_matrix[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False] * n
    safe_sequence = []
    log = [f"Initial Work: {work}"]
    count = 0
    while count < n:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                log.append(f"Process {processes[i]} can be allocated. Need: {need[i]} <= Work: {work}")
                work = [work[j] + allocation[i][j] for j in range(m)]
                finish[i] = True
                safe_sequence.append(processes[i])
                log.append(f"Process {processes[i]} finished. New Work: {work}")
                found = True
                count += 1
        if not found:
            log.append("System is in an UNSAFE state. No process can proceed.")
            return False, [], need, log
    log.append("System is in a SAFE state.")
    return True, safe_sequence, need, log


def detect_deadlock(nodes, edges):
    adj = {n['id']: [] for n in nodes}
    for e in edges:
        if e['source'] in adj:
            adj[e['source']].append(e['target'])
    visited, rec_stack, cycle_path = set(), set(), []

    def find_cycle(u, path):
        nonlocal cycle_path
        visited.add(u)
        rec_stack.add(u)
        path.append(u)
        for v in adj.get(u, []):
            if v not in visited:
                if find_cycle(v, path):
                    return True
            elif v in rec_stack:
                idx = path.index(v)
                cycle_path = path[idx:]
                return True
        rec_stack.discard(u)
        path.pop()
        return False

    for node in nodes:
        if node['id'] not in visited:
            if find_cycle(node['id'], []):
                break
    procs = [nid for nid in cycle_path if any(n['id'] == nid and n['type'] == 'process' for n in nodes)]
    return bool(cycle_path), procs, cycle_path


def recover_deadlock(allocation, available, deadlocked, strategy):
    alloc = [row[:] for row in allocation]
    avail = available[:]
    nr = len(available)
    steps = []
    if strategy == 'terminate-all':
        steps.append(f"Terminating all: {', '.join(deadlocked)}")
        for pid in deadlocked:
            idx = int(pid.replace('P', ''))
            for j in range(nr):
                avail[j] += alloc[idx][j]
                alloc[idx][j] = 0
            steps.append(f"{pid} terminated. Resources released.")
    elif strategy == 'terminate-one-by-one':
        for pid in sorted(deadlocked, key=lambda p: sum(alloc[int(p.replace('P', ''))]), reverse=True):
            idx = int(pid.replace('P', ''))
            for j in range(nr):
                avail[j] += alloc[idx][j]
                alloc[idx][j] = 0
            steps.append(f"{pid} terminated. Available: {avail}")
    elif strategy == 'preemption':
        remaining = list(deadlocked)
        while remaining:
            remaining.sort(key=lambda p: sum(alloc[int(p.replace('P', ''))]))
            victim = remaining.pop(0)
            vi = int(victim.replace('P', ''))
            pre = alloc[vi][:]
            for j in range(nr):
                avail[j] += alloc[vi][j]
                alloc[vi][j] = 0
            steps.append(f"Preempted {pre} from {victim}. Available: {avail}")
            if remaining:
                if all(all(alloc[int(p.replace('P',''))][j] <= avail[j] for j in range(nr)) for p in remaining):
                    steps.append(f"Deadlock resolved! {', '.join(remaining)} can proceed.")
                    break
    return steps, alloc


# ── Data Generators ──

def gen_bankers(n=None, m=None):
    n = n or random.randint(3, 6)
    m = m or random.randint(2, 4)
    procs = [f"P{i}" for i in range(n)]
    res = [chr(65+i) for i in range(m)]
    total = [random.randint(5, 12) for _ in range(m)]
    alloc = [[0]*m for _ in range(n)]
    mx = [[0]*m for _ in range(n)]
    for j in range(m):
        rem = total[j]
        for i in range(n):
            a = random.randint(0, min(rem, total[j]//n+2))
            alloc[i][j] = a
            rem -= a
            mx[i][j] = a + random.randint(0, min(rem+2, total[j]-a))
    avail = [total[j] - sum(alloc[i][j] for i in range(n)) for j in range(m)]
    avail = [max(0, v) for v in avail]
    return procs, res, alloc, mx, avail


PRESETS = {
    'deadlock': {
        'name': 'Deadlock Scenario',
        'nodes': [{'id':'P1','type':'process'},{'id':'P2','type':'process'},{'id':'P3','type':'process'},{'id':'R1','type':'resource'},{'id':'R2','type':'resource'}],
        'edges': [{'source':'P1','target':'R1'},{'source':'R1','target':'P2'},{'source':'P2','target':'R2'},{'source':'R2','target':'P1'},{'source':'P3','target':'R2'}],
    },
    'safe': {
        'name': 'Safe Scenario',
        'nodes': [{'id':'P1','type':'process'},{'id':'P2','type':'process'},{'id':'R1','type':'resource'},{'id':'R2','type':'resource'}],
        'edges': [{'source':'P1','target':'R1'},{'source':'R2','target':'P2'}],
    },
    'complex': {
        'name': 'Complex Deadlock',
        'nodes': [{'id':'P1','type':'process'},{'id':'P2','type':'process'},{'id':'P3','type':'process'},{'id':'R1','type':'resource'},{'id':'R2','type':'resource'},{'id':'R3','type':'resource'}],
        'edges': [{'source':'P1','target':'R1'},{'source':'R1','target':'P2'},{'source':'P2','target':'R2'},{'source':'R2','target':'P3'},{'source':'P3','target':'R3'},{'source':'R3','target':'P1'}],
    },
}

# ══════════════════════════════════════════
# HELPER WIDGETS
# ══════════════════════════════════════════

class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=WHITE, corner_radius=12, border_width=1, border_color=STONE200, **kw)

class SectionTitle(ctk.CTkLabel):
    def __init__(self, master, text, color=STONE800, **kw):
        super().__init__(master, text=text, font=(FONT_FAMILY, 14, "bold"), text_color=color, anchor="w", **kw)

class MatrixTable(ctk.CTkFrame):
    """Editable matrix table widget."""
    def __init__(self, master, title, dot_color, processes, resources, data, editable=True, **kw):
        super().__init__(master, fg_color=WHITE, corner_radius=12, border_width=1, border_color=STONE200, **kw)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16,8))
        ctk.CTkFrame(header, width=8, height=8, corner_radius=4, fg_color=dot_color).pack(side="left", padx=(0,8))
        ctk.CTkLabel(header, text=title, font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(side="left")

        table = ctk.CTkFrame(self, fg_color="transparent")
        table.pack(fill="x", padx=16, pady=(0,16))
        # Header row
        ctk.CTkLabel(table, text="PROCESS", font=(FONT_FAMILY, 10), text_color=STONE400, width=70).grid(row=0, column=0, padx=2, pady=2)
        for j, r in enumerate(resources):
            ctk.CTkLabel(table, text=r, font=(FONT_FAMILY, 10), text_color=STONE400, width=50).grid(row=0, column=j+1, padx=2, pady=2)
        # Data rows
        self.entries = []
        for i, p in enumerate(processes):
            ctk.CTkLabel(table, text=p, font=(FONT_FAMILY, 12), text_color=dot_color, width=70).grid(row=i+1, column=0, padx=2, pady=1)
            row_entries = []
            for j in range(len(resources)):
                if editable:
                    var = tk.StringVar(value=str(data[i][j] if i < len(data) and j < len(data[i]) else 0))
                    e = ctk.CTkEntry(table, textvariable=var, width=50, height=28, font=(FONT_FAMILY, 11),
                                     fg_color=STONE50, border_color=STONE200, corner_radius=6)
                    e.grid(row=i+1, column=j+1, padx=2, pady=1)
                    row_entries.append(var)
                else:
                    val = data[i][j] if i < len(data) and j < len(data[i]) else 0
                    ctk.CTkLabel(table, text=str(val), font=(FONT_FAMILY, 12), text_color=STONE700, width=50).grid(row=i+1, column=j+1, padx=2, pady=1)
                    row_entries.append(None)
            self.entries.append(row_entries)

    def get_data(self):
        result = []
        for row in self.entries:
            r = []
            for var in row:
                try: r.append(int(var.get()) if var else 0)
                except: r.append(0)
            result.append(r)
        return result


# ══════════════════════════════════════════
# PAGE: SYSTEM SETUP
# ══════════════════════════════════════════

class SetupPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        # Title
        ctk.CTkLabel(self, text="System Setup", font=(FONT_FAMILY, 22, "bold"), text_color=STONE800, anchor="w").pack(fill="x", padx=32, pady=(32,4))
        ctk.CTkLabel(self, text="Configure the system parameters and generate resource allocation data", font=(FONT_FAMILY, 12), text_color=STONE500, anchor="w").pack(fill="x", padx=32, pady=(0,20))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=32, pady=(0,16))
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        # Process config card
        pc = Card(cards)
        pc.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        h1 = ctk.CTkFrame(pc, fg_color="transparent")
        h1.pack(fill="x", padx=20, pady=(20,8))
        ctk.CTkLabel(h1, text="⚙", font=(FONT_FAMILY, 16), text_color=ORANGE).pack(side="left", padx=(0,8))
        ctk.CTkLabel(h1, text="Process Configuration", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(side="left")
        ctk.CTkLabel(pc, text="Number of Processes", font=(FONT_FAMILY, 11), text_color=STONE500, anchor="w").pack(fill="x", padx=20)
        self.proc_var = tk.StringVar(value="5")
        ctk.CTkEntry(pc, textvariable=self.proc_var, font=(FONT_FAMILY, 13), fg_color=STONE50, border_color=STONE200, height=38).pack(fill="x", padx=20, pady=(4,4))
        ctk.CTkLabel(pc, text="Processes will be named P0, P1, P2…", font=(FONT_FAMILY, 10), text_color=STONE400, anchor="w").pack(fill="x", padx=20, pady=(0,20))

        # Resource config card
        rc = Card(cards)
        rc.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        h2 = ctk.CTkFrame(rc, fg_color="transparent")
        h2.pack(fill="x", padx=20, pady=(20,8))
        ctk.CTkLabel(h2, text="📦", font=(FONT_FAMILY, 16), text_color=BLUE).pack(side="left", padx=(0,8))
        ctk.CTkLabel(h2, text="Resource Configuration", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(side="left")
        ctk.CTkLabel(rc, text="Number of Resource Types", font=(FONT_FAMILY, 11), text_color=STONE500, anchor="w").pack(fill="x", padx=20)
        self.res_var = tk.StringVar(value="3")
        ctk.CTkEntry(rc, textvariable=self.res_var, font=(FONT_FAMILY, 13), fg_color=STONE50, border_color=STONE200, height=38).pack(fill="x", padx=20, pady=(4,4))
        ctk.CTkLabel(rc, text="Resources will be named A, B, C…", font=(FONT_FAMILY, 10), text_color=STONE400, anchor="w").pack(fill="x", padx=20, pady=(0,20))

        # Buttons
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(0,20))
        ctk.CTkButton(btns, text="✨ Generate System", font=(FONT_FAMILY, 13, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, height=44, corner_radius=10, command=self.generate).pack(side="left", padx=(0,8))
        ctk.CTkButton(btns, text="↻ Reset to Default", font=(FONT_FAMILY, 13, "bold"), fg_color=STONE100, hover_color=STONE200, text_color=STONE700, height=44, corner_radius=10, border_width=1, border_color=STONE200, command=self.reset).pack(side="left")

        self.preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_frame.pack(fill="both", expand=True, padx=32, pady=(0,32))

    def generate(self):
        try:
            n = max(2, min(10, int(self.proc_var.get())))
            m = max(1, min(8, int(self.res_var.get())))
        except: n, m = 5, 3
        procs, res, alloc, mx, avail = gen_bankers(n, m)
        self.app.system = {'processes': procs, 'resources': res, 'allocation': alloc, 'max': mx, 'available': avail}
        self.show_preview()

    def reset(self):
        self.proc_var.set("5")
        self.res_var.set("3")
        self.app.system = None
        for w in self.preview_frame.winfo_children():
            w.destroy()

    def show_preview(self):
        for w in self.preview_frame.winfo_children():
            w.destroy()
        s = self.app.system
        if not s: return
        # Success indicator
        hdr = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        hdr.pack(fill="x", pady=(0,12))
        ctk.CTkFrame(hdr, width=8, height=8, corner_radius=4, fg_color=GREEN).pack(side="left", padx=(0,8))
        ctk.CTkLabel(hdr, text="System Generated Successfully", font=(FONT_FAMILY, 14, "bold"), text_color="#047857").pack(side="left")

        row = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        row.pack(fill="x", pady=(0,16))
        row.columnconfigure((0,1,2), weight=1)
        MatrixTable(row, "Allocation Matrix", ORANGE, s['processes'], s['resources'], s['allocation'], editable=False).grid(row=0, column=0, padx=(0,4), sticky="nsew")
        MatrixTable(row, "Max Matrix", BLUE, s['processes'], s['resources'], s['max'], editable=False).grid(row=0, column=1, padx=4, sticky="nsew")
        # Available
        av_card = Card(row)
        av_card.grid(row=0, column=2, padx=(4,0), sticky="nsew")
        ctk.CTkLabel(av_card, text="AVAILABLE RESOURCES", font=(FONT_FAMILY, 10, "bold"), text_color=AMBER).pack(padx=16, pady=(16,8), anchor="w")
        for i, r in enumerate(s['resources']):
            f = ctk.CTkFrame(av_card, fg_color=STONE50, corner_radius=8, border_width=1, border_color=STONE200)
            f.pack(padx=16, pady=2, fill="x")
            ctk.CTkLabel(f, text=r, font=(FONT_FAMILY, 10), text_color=STONE400).pack(padx=12, pady=(8,0))
            ctk.CTkLabel(f, text=str(s['available'][i]), font=(FONT_FAMILY, 18, "bold"), text_color=STONE800).pack(padx=12, pady=(0,8))


# ══════════════════════════════════════════
# PAGE: BANKER'S ALGORITHM
# ══════════════════════════════════════════

class BankersPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        self.result = None
        s = app.system or {'processes': [f"P{i}" for i in range(5)], 'resources': ['A','B','C'],
                           'allocation': [[0]*3 for _ in range(5)], 'max': [[0]*3 for _ in range(5)], 'available': [0,0,0]}

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32,16))
        ctk.CTkLabel(top, text="Banker's Algorithm", font=(FONT_FAMILY, 22, "bold"), text_color=STONE800).pack(side="left")
        ctk.CTkButton(top, text="▶ Run Safety Check", font=(FONT_FAMILY, 13, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, height=40, corner_radius=10, command=self.run_check).pack(side="right")

        ctk.CTkLabel(self, text="Deadlock prevention through safety state analysis", font=(FONT_FAMILY, 12), text_color=STONE500, anchor="w").pack(fill="x", padx=32, pady=(0,16))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=(0,32))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        self.alloc_table = MatrixTable(left, "Allocation Matrix", ORANGE, s['processes'], s['resources'], s['allocation'])
        self.alloc_table.pack(fill="x", pady=(0,8))
        self.max_table = MatrixTable(left, "Max Matrix", BLUE, s['processes'], s['resources'], s['max'])
        self.max_table.pack(fill="x", pady=(0,8))

        # Available
        av_card = Card(left)
        av_card.pack(fill="x")
        hdr = ctk.CTkFrame(av_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(16,8))
        ctk.CTkFrame(hdr, width=8, height=8, corner_radius=4, fg_color=AMBER).pack(side="left", padx=(0,8))
        ctk.CTkLabel(hdr, text="Available Resources", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(side="left")
        av_row = ctk.CTkFrame(av_card, fg_color="transparent")
        av_row.pack(fill="x", padx=16, pady=(0,16))
        self.avail_vars = []
        for i, r in enumerate(s['resources']):
            f = ctk.CTkFrame(av_row, fg_color="transparent")
            f.pack(side="left", padx=(0,12))
            ctk.CTkLabel(f, text=r, font=(FONT_FAMILY, 10), text_color=STONE400).pack()
            v = tk.StringVar(value=str(s['available'][i]))
            ctk.CTkEntry(f, textvariable=v, width=60, height=32, font=(FONT_FAMILY, 12), fg_color=STONE50, border_color=STONE200, corner_radius=6).pack(pady=(2,0))
            self.avail_vars.append(v)

        self.procs = s['processes']
        self.res = s['resources']
        self.right = ctk.CTkFrame(content, fg_color="transparent")
        self.right.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        self.show_placeholder()

    def show_placeholder(self):
        for w in self.right.winfo_children(): w.destroy()
        ph = ctk.CTkFrame(self.right, fg_color=STONE50, corner_radius=12, border_width=1, border_color=STONE200)
        ph.pack(fill="both", expand=True)
        ctk.CTkLabel(ph, text="🛡", font=(FONT_FAMILY, 32), text_color=STONE400).pack(pady=(60,8))
        ctk.CTkLabel(ph, text="Ready for Analysis", font=(FONT_FAMILY, 14, "bold"), text_color=STONE500).pack()
        ctk.CTkLabel(ph, text="Configure matrices and run the safety\nalgorithm to see results here.", font=(FONT_FAMILY, 11), text_color=STONE400).pack(pady=(4,0))

    def run_check(self):
        alloc = self.alloc_table.get_data()
        mx = self.max_table.get_data()
        avail = [int(v.get() or 0) for v in self.avail_vars]
        safe, seq, need, log = bankers_safety_check(self.procs, self.res, alloc, mx, avail)
        for w in self.right.winfo_children(): w.destroy()

        # Result card
        bg = GREEN_LIGHT if safe else RED_LIGHT
        border = "#a7f3d0" if safe else "#fecaca"
        rc = ctk.CTkFrame(self.right, fg_color=bg, corner_radius=12, border_width=1, border_color=border)
        rc.pack(fill="x", pady=(0,8))
        hdr = ctk.CTkFrame(rc, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(16,8))
        txt = "System is SAFE ✓" if safe else "System is UNSAFE ✗"
        clr = "#047857" if safe else "#b91c1c"
        ctk.CTkLabel(hdr, text=txt, font=(FONT_FAMILY, 16, "bold"), text_color=clr).pack(side="left")
        if safe:
            ctk.CTkLabel(hdr, text="SAFE SEQUENCE FOUND", font=(FONT_FAMILY, 9, "bold"), text_color=WHITE, fg_color=GREEN, corner_radius=4, padx=8, pady=2).pack(side="right")

        if safe:
            sf = ctk.CTkFrame(rc, fg_color="transparent")
            sf.pack(fill="x", padx=16, pady=(0,8))
            for i, p in enumerate(seq):
                chip = ctk.CTkFrame(sf, fg_color=WHITE, corner_radius=6, border_width=1, border_color=STONE200)
                chip.pack(side="left", padx=2)
                ctk.CTkLabel(chip, text=p, font=(FONT_FAMILY, 12), text_color=STONE800).pack(padx=12, pady=6)
                if i < len(seq)-1:
                    ctk.CTkLabel(sf, text="→", font=(FONT_FAMILY, 12), text_color=STONE400).pack(side="left", padx=2)

        # Log
        log_frame = ctk.CTkFrame(rc, fg_color=STONE800, corner_radius=8)
        log_frame.pack(fill="x", padx=16, pady=(0,16))
        log_scroll = ctk.CTkScrollableFrame(log_frame, fg_color=STONE800, height=200)
        log_scroll.pack(fill="x", padx=8, pady=8)
        for i, line in enumerate(log):
            c = STONE400
            if "UNSAFE" in line: c = "#fca5a5"
            elif "SAFE" in line: c = "#6ee7b7"
            elif "finished" in line: c = "#86efac"
            elif "can be" in line: c = "#fde68a"
            ctk.CTkLabel(log_scroll, text=f"[{i+1}] {line}", font=(FONT_FAMILY, 10), text_color=c, anchor="w").pack(fill="x")

        # Need matrix
        MatrixTable(self.right, "Need Matrix (Calculated)", STONE500, self.procs, self.res, need, editable=False).pack(fill="x", pady=(8,0))


# ══════════════════════════════════════════
# PAGE: DEADLOCK DETECTION
# ══════════════════════════════════════════

class DetectionPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        preset = PRESETS['deadlock']
        self.nodes = [n.copy() for n in preset['nodes']]
        self.edges = [e.copy() for e in preset['edges']]
        self.result = None

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32,4))
        ctk.CTkLabel(top, text="Deadlock Detection", font=(FONT_FAMILY, 22, "bold"), text_color=STONE800).pack(side="left")
        ctk.CTkButton(top, text="🔍 Detect Deadlock", font=(FONT_FAMILY, 13, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, height=40, corner_radius=10, command=self.detect).pack(side="right")
        ctk.CTkLabel(self, text="Cycle detection in Resource Allocation Graphs (RAG)", font=(FONT_FAMILY, 12), text_color=STONE500, anchor="w").pack(fill="x", padx=32, pady=(0,16))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=(0,32))
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)

        # Graph canvas
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        graph_card = Card(left)
        graph_card.pack(fill="both", expand=True)
        gh = ctk.CTkFrame(graph_card, fg_color="transparent")
        gh.pack(fill="x", padx=16, pady=(16,8))
        ctk.CTkLabel(gh, text="Resource Allocation Graph", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(side="left")
        legend = ctk.CTkFrame(gh, fg_color="transparent")
        legend.pack(side="right")
        ctk.CTkFrame(legend, width=10, height=10, corner_radius=5, fg_color=BLUE).pack(side="left", padx=(0,4))
        ctk.CTkLabel(legend, text="Process", font=(FONT_FAMILY, 10), text_color=STONE500).pack(side="left", padx=(0,12))
        ctk.CTkFrame(legend, width=10, height=10, corner_radius=5, fg_color=GREEN).pack(side="left", padx=(0,4))
        ctk.CTkLabel(legend, text="Resource", font=(FONT_FAMILY, 10), text_color=STONE500).pack(side="left")

        self.canvas = Canvas(graph_card, bg=WHITE, highlightthickness=0, height=380)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(0,16))
        self.draw_graph()

        # Right panel
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        self.result_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.result_frame.pack(fill="x", pady=(0,8))
        self.show_scan_placeholder()

        # Presets
        pre_card = Card(right)
        pre_card.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(pre_card, text="Quick Presets", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
        for key, p in PRESETS.items():
            ctk.CTkButton(pre_card, text=f"{p['name']}  ({len(p['nodes'])} nodes, {len(p['edges'])} edges)", font=(FONT_FAMILY, 11), fg_color=STONE50, hover_color=STONE100, text_color=STONE600, height=36, corner_radius=8, border_width=1, border_color=STONE200, anchor="w",
                          command=lambda k=key: self.load_preset(k)).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(pre_card, text="↻ Clear Graph", font=(FONT_FAMILY, 11), fg_color=RED_LIGHT, hover_color="#fecaca", text_color=RED, height=36, corner_radius=8, border_width=1, border_color="#fecaca", anchor="w",
                      command=self.clear_graph).pack(fill="x", padx=16, pady=(2,16))

        # Edge management
        edge_card = Card(right)
        edge_card.pack(fill="x")
        ctk.CTkLabel(edge_card, text="Edge Management", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
        ctk.CTkLabel(edge_card, text="ADD EDGE", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, anchor="w")
        ef = ctk.CTkFrame(edge_card, fg_color="transparent")
        ef.pack(fill="x", padx=16, pady=(4,8))
        self.edge_from = ctk.CTkEntry(ef, placeholder_text="From (P1)", width=100, height=32, font=(FONT_FAMILY, 11), fg_color=STONE50, border_color=STONE200)
        self.edge_from.pack(side="left", padx=(0,4))
        self.edge_to = ctk.CTkEntry(ef, placeholder_text="To (R1)", width=100, height=32, font=(FONT_FAMILY, 11), fg_color=STONE50, border_color=STONE200)
        self.edge_to.pack(side="left", padx=(0,4))
        ctk.CTkButton(ef, text="+", width=32, height=32, font=(FONT_FAMILY, 14), fg_color=STONE100, hover_color=STONE200, text_color=STONE600, corner_radius=6, border_width=1, border_color=STONE200,
                      command=self.add_edge).pack(side="left")

        ctk.CTkLabel(edge_card, text="CURRENT EDGES", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(8,4), anchor="w")
        self.edge_list = ctk.CTkScrollableFrame(edge_card, fg_color="transparent", height=120)
        self.edge_list.pack(fill="x", padx=16, pady=(0,16))
        self.refresh_edge_list()

    def show_scan_placeholder(self):
        for w in self.result_frame.winfo_children(): w.destroy()
        ph = ctk.CTkFrame(self.result_frame, fg_color=STONE50, corner_radius=12, border_width=1, border_color=STONE200)
        ph.pack(fill="x")
        ctk.CTkLabel(ph, text="🔍", font=(FONT_FAMILY, 28), text_color=STONE400).pack(pady=(24,4))
        ctk.CTkLabel(ph, text="Scan Required", font=(FONT_FAMILY, 13, "bold"), text_color=STONE500).pack()
        ctk.CTkLabel(ph, text="Click detect to analyze the graph.", font=(FONT_FAMILY, 10), text_color=STONE400).pack(pady=(2,24))

    def draw_graph(self, cycle_path=None):
        self.canvas.delete("all")
        w, h = 600, 370
        positions = {}
        n = len(self.nodes)
        if n == 0: return
        cx, cy = w//2, h//2
        for i, node in enumerate(self.nodes):
            angle = 2 * math.pi * i / n - math.pi/2
            r = min(w, h) * 0.35
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            positions[node['id']] = (x, y)

        cycle_edges = set()
        if cycle_path:
            for i in range(len(cycle_path)):
                cycle_edges.add((cycle_path[i], cycle_path[(i+1) % len(cycle_path)]))

        for e in self.edges:
            s, t = e['source'], e['target']
            if s in positions and t in positions:
                x1, y1 = positions[s]
                x2, y2 = positions[t]
                in_cycle = (s, t) in cycle_edges
                color = RED if in_cycle else STONE400
                width = 3 if in_cycle else 1.5
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST, arrowshape=(10,12,5))

        for node in self.nodes:
            x, y = positions[node['id']]
            r = 28
            if node['type'] == 'process':
                in_cycle = cycle_path and node['id'] in cycle_path
                fill = "#fee2e2" if in_cycle else "#dbeafe"
                outline = RED if in_cycle else BLUE
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=outline, width=2)
            else:
                fill = "#d1fae5"
                outline = GREEN
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=outline, width=2)
            self.canvas.create_text(x, y, text=node['id'], font=(FONT_FAMILY, 11, "bold"), fill=STONE800)

    def detect(self):
        dl, procs, cycle = detect_deadlock(self.nodes, self.edges)
        self.draw_graph(cycle if dl else None)
        for w in self.result_frame.winfo_children(): w.destroy()
        if dl:
            rc = ctk.CTkFrame(self.result_frame, fg_color=RED_LIGHT, corner_radius=12, border_width=1, border_color="#fecaca")
            rc.pack(fill="x")
            ctk.CTkLabel(rc, text="⚠ Deadlock Detected!", font=(FONT_FAMILY, 15, "bold"), text_color="#b91c1c").pack(padx=16, pady=(16,8), anchor="w")
            ctk.CTkLabel(rc, text="CYCLE PATH", font=(FONT_FAMILY, 9, "bold"), text_color=STONE500).pack(padx=16, anchor="w")
            pf = ctk.CTkFrame(rc, fg_color="transparent")
            pf.pack(fill="x", padx=16, pady=(4,8))
            for i, nid in enumerate(cycle):
                bg = BLUE_LIGHT if nid.startswith('P') else GREEN_LIGHT
                tc = BLUE if nid.startswith('P') else GREEN
                chip = ctk.CTkFrame(pf, fg_color=bg, corner_radius=4, border_width=1, border_color=STONE200)
                chip.pack(side="left", padx=1)
                ctk.CTkLabel(chip, text=nid, font=(FONT_FAMILY, 10), text_color=tc).pack(padx=8, pady=4)
                if i < len(cycle)-1:
                    ctk.CTkLabel(pf, text="→", font=(FONT_FAMILY, 10), text_color=STONE400).pack(side="left", padx=1)
            ctk.CTkLabel(rc, text="PROCESSES INVOLVED", font=(FONT_FAMILY, 9, "bold"), text_color=STONE500).pack(padx=16, pady=(4,0), anchor="w")
            pf2 = ctk.CTkFrame(rc, fg_color="transparent")
            pf2.pack(fill="x", padx=16, pady=(4,16))
            for p in procs:
                chip2 = ctk.CTkFrame(pf2, fg_color="#fee2e2", corner_radius=6, border_width=1, border_color="#fecaca")
                chip2.pack(side="left", padx=2)
                ctk.CTkLabel(chip2, text=p, font=(FONT_FAMILY, 11, "bold"), text_color=RED).pack(padx=10, pady=4)
        else:
            rc = ctk.CTkFrame(self.result_frame, fg_color=GREEN_LIGHT, corner_radius=12, border_width=1, border_color="#a7f3d0")
            rc.pack(fill="x")
            ctk.CTkLabel(rc, text="✓ No Deadlock Found", font=(FONT_FAMILY, 15, "bold"), text_color="#047857").pack(padx=16, pady=(16,4), anchor="w")
            ctk.CTkLabel(rc, text="No cycles found in the RAG.", font=(FONT_FAMILY, 11), text_color=STONE600).pack(padx=16, pady=(0,16), anchor="w")

    def load_preset(self, key):
        p = PRESETS[key]
        self.nodes = [n.copy() for n in p['nodes']]
        self.edges = [e.copy() for e in p['edges']]
        self.draw_graph()
        self.refresh_edge_list()
        self.show_scan_placeholder()

    def clear_graph(self):
        self.nodes, self.edges = [], []
        self.draw_graph()
        self.refresh_edge_list()
        self.show_scan_placeholder()

    def add_edge(self):
        f = self.edge_from.get().strip().upper()
        t = self.edge_to.get().strip().upper()
        if not f or not t: return
        for nid in [f, t]:
            if not any(n['id'] == nid for n in self.nodes):
                self.nodes.append({'id': nid, 'type': 'process' if nid.startswith('P') else 'resource'})
        self.edges.append({'source': f, 'target': t})
        self.edge_from.delete(0, 'end')
        self.edge_to.delete(0, 'end')
        self.draw_graph()
        self.refresh_edge_list()

    def refresh_edge_list(self):
        for w in self.edge_list.winfo_children(): w.destroy()
        for i, e in enumerate(self.edges):
            s = f"{e['source']} → {e['target']}"
            ctk.CTkLabel(self.edge_list, text=s, font=(FONT_FAMILY, 10), text_color=STONE600, fg_color=STONE50, corner_radius=6, padx=10, pady=4, anchor="w").pack(fill="x", pady=1)


# ══════════════════════════════════════════
# PAGE: RECOVERY
# ══════════════════════════════════════════

class RecoveryPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        self.strategy = 'terminate-one-by-one'
        self.deadlocked = ['P0', 'P1']
        self.num_res = 3

        ctk.CTkLabel(self, text="Deadlock Recovery", font=(FONT_FAMILY, 22, "bold"), text_color=STONE800, anchor="w").pack(fill="x", padx=32, pady=(32,4))
        ctk.CTkLabel(self, text="Strategies to break cycles and restore system safety", font=(FONT_FAMILY, 12), text_color=STONE500, anchor="w").pack(fill="x", padx=32, pady=(0,16))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=(0,32))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)

        # Left: Strategy
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        strat_card = Card(left)
        strat_card.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(strat_card, text="Select Strategy", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")

        strategies = [('terminate-all', '🗑 Terminate All', 'Stop all processes simultaneously.'),
                      ('terminate-one-by-one', '⚡ One-by-One', 'Terminate sequentially until cycle is broken.'),
                      ('preemption', '↻ Resource Preemption', 'Take resources from processes.')]
        self.strat_btns = []
        for sid, name, desc in strategies:
            btn = ctk.CTkButton(strat_card, text=f"{name}\n{desc}", font=(FONT_FAMILY, 11), height=60, corner_radius=8,
                                fg_color=ORANGE_LIGHT if sid == self.strategy else STONE50,
                                hover_color=STONE100, text_color=STONE800 if sid == self.strategy else STONE600,
                                border_width=1, border_color=ORANGE if sid == self.strategy else STONE200, anchor="w",
                                command=lambda s=sid: self.set_strategy(s))
            btn.pack(fill="x", padx=16, pady=2)
            self.strat_btns.append((sid, btn))

        ctk.CTkButton(strat_card, text="↻ Execute Recovery", font=(FONT_FAMILY, 13, "bold"), fg_color=GREEN, hover_color="#059669",
                      height=44, corner_radius=10, command=self.execute).pack(fill="x", padx=16, pady=(16,16))

        # Right
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, padx=(8,0), sticky="nsew")

        # Deadlocked processes
        dp_card = Card(right)
        dp_card.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(dp_card, text="Deadlocked Processes", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
        add_f = ctk.CTkFrame(dp_card, fg_color="transparent")
        add_f.pack(fill="x", padx=16, pady=(0,8))
        self.new_proc = ctk.CTkEntry(add_f, placeholder_text="Process ID (e.g. P3)", height=32, font=(FONT_FAMILY, 11), fg_color=STONE50, border_color=STONE200)
        self.new_proc.pack(side="left", fill="x", expand=True, padx=(0,4))
        ctk.CTkButton(add_f, text="+ Add", width=70, height=32, font=(FONT_FAMILY, 11, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, command=self.add_proc).pack(side="left")
        self.proc_frame = ctk.CTkFrame(dp_card, fg_color="transparent")
        self.proc_frame.pack(fill="x", padx=16, pady=(0,16))
        self.refresh_procs()

        # Allocation matrix
        self.alloc_data = [[1,0,2],[0,1,0]]
        self.avail_data = [0,0,0]
        self.matrix_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.matrix_frame.pack(fill="x", pady=(0,8))
        self.rebuild_matrix()

        # Available
        self.avail_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.avail_frame.pack(fill="x", pady=(0,8))
        self.rebuild_avail()

        # Result
        self.result_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.result_frame.pack(fill="x")

    def set_strategy(self, s):
        self.strategy = s
        for sid, btn in self.strat_btns:
            if sid == s:
                btn.configure(fg_color=ORANGE_LIGHT, text_color=STONE800, border_color=ORANGE)
            else:
                btn.configure(fg_color=STONE50, text_color=STONE600, border_color=STONE200)

    def add_proc(self):
        pid = self.new_proc.get().strip().upper()
        if pid and pid not in self.deadlocked:
            self.deadlocked.append(pid)
            self.alloc_data.append([0]*self.num_res)
            self.new_proc.delete(0, 'end')
            self.refresh_procs()
            self.rebuild_matrix()

    def remove_proc(self, idx):
        self.deadlocked.pop(idx)
        self.alloc_data.pop(idx)
        self.refresh_procs()
        self.rebuild_matrix()

    def refresh_procs(self):
        for w in self.proc_frame.winfo_children(): w.destroy()
        for i, p in enumerate(self.deadlocked):
            f = ctk.CTkFrame(self.proc_frame, fg_color=RED_LIGHT, corner_radius=8, border_width=1, border_color="#fecaca")
            f.pack(side="left", padx=(0,4), pady=2)
            ctk.CTkLabel(f, text=f"{p}\nBLOCKED", font=(FONT_FAMILY, 10, "bold"), text_color=RED).pack(side="left", padx=8, pady=6)
            ctk.CTkButton(f, text="✕", width=24, height=24, font=(FONT_FAMILY, 10), fg_color="transparent", hover_color="#fecaca", text_color=STONE400, command=lambda idx=i: self.remove_proc(idx)).pack(side="left", padx=(0,4))

    def rebuild_matrix(self):
        for w in self.matrix_frame.winfo_children(): w.destroy()
        res_labels = [chr(65+i) for i in range(self.num_res)]
        self.alloc_table = MatrixTable(self.matrix_frame, "Allocation Matrix", ORANGE, self.deadlocked, res_labels, self.alloc_data)
        self.alloc_table.pack(fill="x")

    def rebuild_avail(self):
        for w in self.avail_frame.winfo_children(): w.destroy()
        av_card = Card(self.avail_frame)
        av_card.pack(fill="x")
        ctk.CTkLabel(av_card, text="Available Resources", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
        af = ctk.CTkFrame(av_card, fg_color="transparent")
        af.pack(fill="x", padx=16, pady=(0,16))
        self.avail_vars = []
        for i in range(self.num_res):
            ff = ctk.CTkFrame(af, fg_color="transparent")
            ff.pack(side="left", padx=(0,8))
            ctk.CTkLabel(ff, text=chr(65+i), font=(FONT_FAMILY, 10), text_color=STONE400).pack()
            v = tk.StringVar(value=str(self.avail_data[i]))
            ctk.CTkEntry(ff, textvariable=v, width=60, height=32, font=(FONT_FAMILY, 12), fg_color=STONE50, border_color=STONE200).pack()
            self.avail_vars.append(v)

    def execute(self):
        alloc_data = self.alloc_table.get_data()
        avail = [int(v.get() or 0) for v in self.avail_vars]
        max_idx = max(int(p.replace('P','')) for p in self.deadlocked) + 1
        full_alloc = [[0]*self.num_res for _ in range(max_idx)]
        for i, pid in enumerate(self.deadlocked):
            idx = int(pid.replace('P',''))
            if idx < max_idx and i < len(alloc_data):
                full_alloc[idx] = alloc_data[i]
        steps, _ = recover_deadlock(full_alloc, avail, self.deadlocked, self.strategy)

        for w in self.result_frame.winfo_children(): w.destroy()
        rc = ctk.CTkFrame(self.result_frame, fg_color=GREEN_LIGHT, corner_radius=12, border_width=1, border_color="#a7f3d0")
        rc.pack(fill="x")
        ctk.CTkLabel(rc, text="✓ Recovery Log", font=(FONT_FAMILY, 14, "bold"), text_color="#047857").pack(padx=16, pady=(16,8), anchor="w")
        for i, step in enumerate(steps):
            sf = ctk.CTkFrame(rc, fg_color="transparent")
            sf.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(sf, text=str(i+1), font=(FONT_FAMILY, 9, "bold"), text_color="#047857", fg_color="#a7f3d0", corner_radius=10, width=22, height=22).pack(side="left", padx=(0,8))
            ctk.CTkLabel(sf, text=step, font=(FONT_FAMILY, 11), text_color=STONE700, anchor="w", wraplength=400).pack(side="left", fill="x")
        # Footer
        ft = ctk.CTkFrame(rc, fg_color="transparent")
        ft.pack(fill="x", padx=16, pady=(8,16))
        ctk.CTkLabel(ft, text=f"Strategy: {self.strategy}", font=(FONT_FAMILY, 10), text_color=STONE500).pack(side="left")
        ctk.CTkFrame(ft, width=8, height=8, corner_radius=4, fg_color=GREEN).pack(side="right", padx=(0,4))
        ctk.CTkLabel(ft, text="SYSTEM SAFE", font=(FONT_FAMILY, 9, "bold"), text_color="#047857").pack(side="right")


# ══════════════════════════════════════════
# PAGE: SIMULATION ENGINE
# ══════════════════════════════════════════

class SimulationPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        self.running = False
        self.speed = 50
        self.logs = []
        self.stats = {'running': 0, 'blocked': 0, 'steps': 0, 'status': 'Idle'}

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32,4))
        ctk.CTkLabel(top, text="Simulation Engine", font=(FONT_FAMILY, 22, "bold"), text_color=STONE800).pack(side="left")
        btn_f = ctk.CTkFrame(top, fg_color="transparent")
        btn_f.pack(side="right")
        ctk.CTkButton(btn_f, text="▶ Run Once", font=(FONT_FAMILY, 12, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, height=38, corner_radius=8, width=100, command=self.run_once).pack(side="left", padx=2)
        self.auto_btn = ctk.CTkButton(btn_f, text="▶ Auto-Run", font=(FONT_FAMILY, 12, "bold"), fg_color=GREEN, hover_color="#059669", height=38, corner_radius=8, width=110, command=self.toggle_auto)
        self.auto_btn.pack(side="left", padx=2)
        ctk.CTkButton(btn_f, text="↻ Reset", font=(FONT_FAMILY, 12, "bold"), fg_color=STONE100, hover_color=STONE200, text_color=STONE700, height=38, corner_radius=8, width=80, border_width=1, border_color=STONE200, command=self.reset).pack(side="left", padx=2)

        ctk.CTkLabel(self, text="Real-time deadlock scenario simulation using Banker's Algorithm", font=(FONT_FAMILY, 12), text_color=STONE500, anchor="w").pack(fill="x", padx=32, pady=(0,16))

        # Stats cards
        stats_f = ctk.CTkFrame(self, fg_color="transparent")
        stats_f.pack(fill="x", padx=32, pady=(0,12))
        stats_f.columnconfigure((0,1,2,3), weight=1)
        self.stat_labels = {}
        stat_defs = [('running', 'Running Processes', '0', BLUE), ('blocked', 'Blocked Processes', '0', RED),
                     ('steps', 'Simulations Run', '0', GREEN), ('status', 'System Health', 'Idle', STONE500)]
        for i, (key, label, val, color) in enumerate(stat_defs):
            c = Card(stats_f)
            c.grid(row=0, column=i, padx=4, sticky="nsew")
            ctk.CTkLabel(c, text=label, font=(FONT_FAMILY, 11), text_color=STONE500).pack(padx=16, pady=(16,4), anchor="w")
            lbl = ctk.CTkLabel(c, text=val, font=(FONT_FAMILY, 22, "bold"), text_color=color)
            lbl.pack(padx=16, pady=(0,16), anchor="e")
            self.stat_labels[key] = lbl

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=(0,32))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)

        # Config
        cfg_card = Card(body)
        cfg_card.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        ctk.CTkLabel(cfg_card, text="Configuration", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
        ctk.CTkLabel(cfg_card, text="Number of Processes", font=(FONT_FAMILY, 11), text_color=STONE500).pack(padx=16, anchor="w")
        self.sim_procs = tk.StringVar(value="5")
        ctk.CTkEntry(cfg_card, textvariable=self.sim_procs, height=36, font=(FONT_FAMILY, 13), fg_color=STONE50, border_color=STONE200).pack(fill="x", padx=16, pady=(4,8))
        ctk.CTkLabel(cfg_card, text="Number of Resources", font=(FONT_FAMILY, 11), text_color=STONE500).pack(padx=16, anchor="w")
        self.sim_res = tk.StringVar(value="3")
        ctk.CTkEntry(cfg_card, textvariable=self.sim_res, height=36, font=(FONT_FAMILY, 13), fg_color=STONE50, border_color=STONE200).pack(fill="x", padx=16, pady=(4,8))

        ctk.CTkLabel(cfg_card, text="Auto-Run Speed", font=(FONT_FAMILY, 11), text_color=STONE500).pack(padx=16, anchor="w")
        self.speed_lbl = ctk.CTkLabel(cfg_card, text="50%", font=(FONT_FAMILY, 11), text_color=ORANGE)
        self.speed_lbl.pack(padx=16, anchor="e")
        self.speed_slider = ctk.CTkSlider(cfg_card, from_=10, to=90, number_of_steps=8, button_color=ORANGE, button_hover_color=ORANGE_HOVER, progress_color=ORANGE, command=self.on_speed)
        self.speed_slider.set(50)
        self.speed_slider.pack(fill="x", padx=16, pady=(0,12))

        info = ctk.CTkFrame(cfg_card, fg_color=ORANGE_LIGHT, corner_radius=8, border_width=1, border_color="#fed7aa")
        info.pack(fill="x", padx=16, pady=(0,16))
        ctk.CTkLabel(info, text="HOW IT WORKS", font=(FONT_FAMILY, 9, "bold"), text_color="#c2410c").pack(padx=12, pady=(8,2), anchor="w")
        ctk.CTkLabel(info, text="Each simulation generates a random system,\nthen simulates resource requests step-by-step\nusing Banker's Algorithm. Unsafe requests\nare automatically denied.", font=(FONT_FAMILY, 10), text_color=STONE500, wraplength=250, justify="left").pack(padx=12, pady=(0,8), anchor="w")

        # Terminal log
        term = ctk.CTkFrame(body, fg_color=STONE900, corner_radius=12, border_width=1, border_color=STONE700)
        term.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        term_hdr = ctk.CTkFrame(term, fg_color=STONE800, corner_radius=0)
        term_hdr.pack(fill="x")
        ctk.CTkLabel(term_hdr, text="〉 SIMULATION LOG", font=(FONT_FAMILY, 11, "bold"), text_color=STONE200).pack(side="left", padx=16, pady=10)
        dots = ctk.CTkFrame(term_hdr, fg_color="transparent")
        dots.pack(side="right", padx=12)
        for c in [RED, AMBER, GREEN]:
            ctk.CTkFrame(dots, width=10, height=10, corner_radius=5, fg_color=c).pack(side="left", padx=2)

        self.log_frame = ctk.CTkScrollableFrame(term, fg_color=STONE900, height=350)
        self.log_frame.pack(fill="both", expand=True, padx=8, pady=8)
        ctk.CTkLabel(self.log_frame, text='Click "Run Once" or "Auto-Run" to start simulation...', font=(FONT_FAMILY, 11), text_color=STONE600).pack(pady=100)

    def on_speed(self, val):
        self.speed = int(val)
        self.speed_lbl.configure(text=f"{self.speed}%")

    def run_once(self):
        threading.Thread(target=self._simulate, daemon=True).start()

    def toggle_auto(self):
        self.running = not self.running
        if self.running:
            self.auto_btn.configure(text="⏸ Pause", fg_color=AMBER, hover_color="#d97706")
            threading.Thread(target=self._auto_run, daemon=True).start()
        else:
            self.auto_btn.configure(text="▶ Auto-Run", fg_color=GREEN, hover_color="#059669")

    def _auto_run(self):
        while self.running:
            self._simulate()
            delay = max(0.5, (100 - self.speed) * 0.04)
            time.sleep(delay)

    def reset(self):
        self.running = False
        self.auto_btn.configure(text="▶ Auto-Run", fg_color=GREEN, hover_color="#059669")
        self.logs = []
        self.stats = {'running': 0, 'blocked': 0, 'steps': 0, 'status': 'Idle'}
        self._update_ui()

    def _simulate(self):
        try:
            np_ = max(2, min(10, int(self.sim_procs.get())))
            nr_ = max(1, min(6, int(self.sim_res.get())))
        except: np_, nr_ = 5, 3
        procs, res, alloc, mx, avail = gen_bankers(np_, nr_)
        total_steps = np_ * 3
        new_logs = [f"--- Simulation #{self.stats['steps']+1} ({np_}P, {nr_}R) ---"]
        for step in range(total_steps):
            pi = random.randint(0, np_-1)
            ri = random.randint(0, nr_-1)
            need = mx[pi][ri] - alloc[pi][ri]
            if need > 0 and avail[ri] > 0:
                amt = min(need, avail[ri], random.randint(1,2))
                alloc[pi][ri] += amt
                avail[ri] -= amt
                safe, seq, _, _ = bankers_safety_check(procs, res, alloc, mx, avail)
                if safe:
                    new_logs.append(f"[Step {step+1}] ✅ Granted {amt}× {res[ri]} to {procs[pi]}. SAFE")
                else:
                    alloc[pi][ri] -= amt
                    avail[ri] += amt
                    new_logs.append(f"[Step {step+1}] ❌ Denied {amt}× {res[ri]} to {procs[pi]}. UNSAFE")
            else:
                new_logs.append(f"[Step {step+1}] ⏭ {procs[pi]} — no need for {res[ri]}")

        safe, seq, _, _ = bankers_safety_check(procs, res, alloc, mx, avail)
        running = [p for i,p in enumerate(procs) if any(alloc[i][j]>0 for j in range(nr_))]
        self.stats['running'] = len(running)
        self.stats['blocked'] = 0 if safe else np_
        self.stats['steps'] += 1
        self.stats['status'] = 'Safe' if safe else 'Unsafe'
        self.logs = new_logs + self.logs
        self.logs = self.logs[:100]
        try: self.after(0, self._update_ui)
        except: pass

    def _update_ui(self):
        self.stat_labels['running'].configure(text=str(self.stats['running']))
        self.stat_labels['blocked'].configure(text=str(self.stats['blocked']))
        self.stat_labels['steps'].configure(text=str(self.stats['steps']))
        self.stat_labels['status'].configure(text=self.stats['status'],
            text_color=GREEN if self.stats['status']=='Safe' else RED if self.stats['status']=='Unsafe' else STONE500)
        for w in self.log_frame.winfo_children(): w.destroy()
        if not self.logs:
            ctk.CTkLabel(self.log_frame, text='Click "Run Once" or "Auto-Run" to start...', font=(FONT_FAMILY, 11), text_color=STONE600).pack(pady=100)
            return
        for line in self.logs:
            if 'Denied' in line or 'UNSAFE' in line:
                c, bg = "#fca5a5", "#7f1d1d"
            elif 'Granted' in line or 'SAFE' in line:
                c, bg = "#6ee7b7", "transparent"
            elif '---' in line:
                c, bg = "#93c5fd", "transparent"
            else:
                c, bg = STONE500, "transparent"
            ctk.CTkLabel(self.log_frame, text=line, font=(FONT_FAMILY, 10), text_color=c, anchor="w").pack(fill="x", pady=1)


# ══════════════════════════════════════════
# PAGE: RAG VISUALIZER
# ══════════════════════════════════════════

class RAGVisualizerPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        self.nodes = [{'id':'P1','type':'process','x':400,'y':150},{'id':'R1','type':'resource','x':400,'y':350}]
        self.edges = []
        self.drag_node = None

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32,4))
        ctk.CTkLabel(top, text="RAG Visualizer — Interactive Deadlock Detection", font=(FONT_FAMILY, 14), text_color=STONE500).pack(side="left")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=(16,32))
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=3)
        content.columnconfigure(2, weight=1)

        # Left: Node library
        lib = Card(content)
        lib.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        ctk.CTkLabel(lib, text="NODE LIBRARY", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(16,8), anchor="w")
        ctk.CTkButton(lib, text="⚙ Process", font=(FONT_FAMILY, 11), fg_color=STONE50, hover_color=STONE100, text_color=STONE700, height=36, corner_radius=8, border_width=1, border_color=STONE200, command=self.add_process).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(lib, text="📦 Resource", font=(FONT_FAMILY, 11), fg_color=STONE50, hover_color=STONE100, text_color=STONE700, height=36, corner_radius=8, border_width=1, border_color=STONE200, command=self.add_resource).pack(fill="x", padx=16, pady=2)

        ctk.CTkLabel(lib, text="SCENARIOS", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(16,4), anchor="w")
        ctk.CTkButton(lib, text="⚠ Load Deadlock", font=(FONT_FAMILY, 11), fg_color=RED_LIGHT, hover_color="#fecaca", text_color=RED, height=36, corner_radius=8, border_width=1, border_color="#fecaca", command=lambda: self.load_scenario('deadlock')).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(lib, text="✓ Load Safe", font=(FONT_FAMILY, 11), fg_color=GREEN_LIGHT, hover_color="#a7f3d0", text_color=GREEN, height=36, corner_radius=8, border_width=1, border_color="#a7f3d0", command=lambda: self.load_scenario('safe')).pack(fill="x", padx=16, pady=2)

        ctk.CTkLabel(lib, text="INSTRUCTIONS", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(16,4), anchor="w")
        instructions = "1. Add nodes from library\n2. Connect with edges below\n3. Process→Resource = Request\n4. Resource→Process = Allocation\n5. Click Run Check to detect"
        ctk.CTkLabel(lib, text=instructions, font=(FONT_FAMILY, 10), text_color=STONE500, justify="left", wraplength=160).pack(padx=16, pady=(0,16), anchor="w")

        # Center: Canvas
        canvas_card = Card(content)
        canvas_card.grid(row=0, column=1, padx=4, sticky="nsew")
        self.canvas = Canvas(canvas_card, bg=WHITE, highlightthickness=0, height=450, width=500)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.draw_rag()

        # Right: Controls
        ctrl = Card(content)
        ctrl.grid(row=0, column=2, padx=(8,0), sticky="nsew")
        ctk.CTkLabel(ctrl, text="SIMULATION", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(16,4), anchor="w")
        ctk.CTkButton(ctrl, text="▶ Run Check", font=(FONT_FAMILY, 13, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, height=40, corner_radius=10, command=self.run_check).pack(fill="x", padx=16, pady=(0,8))

        ctk.CTkLabel(ctrl, text="PROPERTIES", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(8,4), anchor="w")
        self.prop_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        self.prop_frame.pack(fill="x", padx=16, pady=(0,8))
        ctk.CTkLabel(self.prop_frame, text="Select a node to\nedit properties.", font=(FONT_FAMILY, 10), text_color=STONE400).pack(pady=16)

        ctk.CTkLabel(ctrl, text="ADD EDGE", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=16, pady=(8,4), anchor="w")
        ef = ctk.CTkFrame(ctrl, fg_color="transparent")
        ef.pack(fill="x", padx=16)
        self.ef_from = ctk.CTkEntry(ef, placeholder_text="From", width=70, height=28, font=(FONT_FAMILY, 10), fg_color=STONE50, border_color=STONE200)
        self.ef_from.pack(side="left", padx=(0,4))
        self.ef_to = ctk.CTkEntry(ef, placeholder_text="To", width=70, height=28, font=(FONT_FAMILY, 10), fg_color=STONE50, border_color=STONE200)
        self.ef_to.pack(side="left", padx=(0,4))
        ctk.CTkButton(ef, text="+", width=28, height=28, font=(FONT_FAMILY, 12), fg_color=STONE100, hover_color=STONE200, text_color=STONE600, command=self.add_edge).pack(side="left")

        self.result_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        self.result_frame.pack(fill="x", padx=16, pady=(8,16))

    def add_process(self):
        n = sum(1 for nd in self.nodes if nd['type']=='process') + 1
        self.nodes.append({'id':f'P{n}','type':'process','x':200+n*60,'y':150})
        self.draw_rag()

    def add_resource(self):
        n = sum(1 for nd in self.nodes if nd['type']=='resource') + 1
        self.nodes.append({'id':f'R{n}','type':'resource','x':200+n*60,'y':350})
        self.draw_rag()

    def load_scenario(self, key):
        p = PRESETS[key]
        self.nodes = []
        n = len(p['nodes'])
        for i, nd in enumerate(p['nodes']):
            angle = 2*math.pi*i/n - math.pi/2
            x = 300 + 150*math.cos(angle)
            y = 250 + 120*math.sin(angle)
            self.nodes.append({'id':nd['id'],'type':nd['type'],'x':x,'y':y})
        self.edges = [e.copy() for e in p['edges']]
        self.draw_rag()

    def add_edge(self):
        f = self.ef_from.get().strip().upper()
        t = self.ef_to.get().strip().upper()
        if f and t:
            self.edges.append({'source':f,'target':t})
            self.ef_from.delete(0,'end')
            self.ef_to.delete(0,'end')
            self.draw_rag()

    def draw_rag(self):
        self.canvas.delete("all")
        pos = {n['id']:(n['x'],n['y']) for n in self.nodes}
        for e in self.edges:
            s, t = e['source'], e['target']
            if s in pos and t in pos:
                self.canvas.create_line(pos[s][0],pos[s][1],pos[t][0],pos[t][1], fill=STONE400, width=1.5, arrow=tk.LAST, arrowshape=(10,12,5))
        for nd in self.nodes:
            x, y, r = nd['x'], nd['y'], 30
            if nd['type'] == 'process':
                self.canvas.create_oval(x-r,y-r,x+r,y+r, fill="#dbeafe", outline=BLUE, width=2)
            else:
                self.canvas.create_oval(x-r,y-r,x+r,y+r, fill="#d1fae5", outline=GREEN, width=2)
            self.canvas.create_text(x, y-6, text=nd['id'], font=(FONT_FAMILY, 11, "bold"), fill=STONE800)
            self.canvas.create_text(x, y+10, text=nd['type'].upper(), font=(FONT_FAMILY, 7), fill=STONE400)

    def on_click(self, event):
        for nd in self.nodes:
            if abs(event.x-nd['x'])<30 and abs(event.y-nd['y'])<30:
                self.drag_node = nd
                for w in self.prop_frame.winfo_children(): w.destroy()
                ctk.CTkLabel(self.prop_frame, text=f"{nd['id']} ({nd['type']})", font=(FONT_FAMILY, 12, "bold"), text_color=STONE800).pack(anchor="w")
                return

    def on_drag(self, event):
        if self.drag_node:
            self.drag_node['x'] = event.x
            self.drag_node['y'] = event.y
            self.draw_rag()

    def on_release(self, event):
        self.drag_node = None

    def run_check(self):
        clean = [{'id':n['id'],'type':n['type']} for n in self.nodes]
        dl, procs, cycle = detect_deadlock(clean, self.edges)
        for w in self.result_frame.winfo_children(): w.destroy()
        if dl:
            ctk.CTkLabel(self.result_frame, text="⚠ DEADLOCK!", font=(FONT_FAMILY, 13, "bold"), text_color=RED).pack(anchor="w")
            ctk.CTkLabel(self.result_frame, text=" → ".join(cycle), font=(FONT_FAMILY, 10), text_color=STONE600, wraplength=180).pack(anchor="w")
        else:
            ctk.CTkLabel(self.result_frame, text="✓ No Deadlock", font=(FONT_FAMILY, 13, "bold"), text_color=GREEN).pack(anchor="w")


# ══════════════════════════════════════════
# PAGE: LIVE PROCESS MONITOR
# ══════════════════════════════════════════

class ProcessMonitorPage(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=STONE50)
        self.app = app
        self._alive = True
        self._auto_refresh = False
        self._refresh_interval = 2000  # ms

        ctk.CTkLabel(self, text="Live Process Monitor", font=(FONT_FAMILY, 22, "bold"), text_color=STONE800, anchor="w").pack(fill="x", padx=32, pady=(32,4))
        ctk.CTkLabel(self, text="Real-time process scanning & deadlock detection on your system", font=(FONT_FAMILY, 12), text_color=STONE500, anchor="w").pack(fill="x", padx=32, pady=(0,16))

        if not HAS_PSUTIL:
            Card(self).pack(fill="x", padx=32, pady=16)
            ctk.CTkLabel(self, text="psutil not installed. Run: pip install psutil", font=(FONT_FAMILY, 14), text_color=RED).pack(padx=32, pady=32)
            return

        # Action buttons
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(0,12))
        ctk.CTkButton(btns, text="📡 Scan Processes", font=(FONT_FAMILY, 12, "bold"), fg_color=ORANGE, hover_color=ORANGE_HOVER, height=40, corner_radius=10, command=self.scan_processes).pack(side="left", padx=(0,8))
        ctk.CTkButton(btns, text="🔍 Detect Deadlocks", font=(FONT_FAMILY, 12, "bold"), fg_color=BLUE, hover_color="#2563eb", height=40, corner_radius=10, command=self.detect_deadlocks).pack(side="left", padx=(0,8))
        ctk.CTkButton(btns, text="🖥 System Overview", font=(FONT_FAMILY, 12, "bold"), fg_color=GREEN, hover_color="#059669", height=40, corner_radius=10, command=self.start_live_overview).pack(side="left", padx=(0,8))
        self.live_btn = ctk.CTkButton(btns, text="🔴 Live Mode: OFF", font=(FONT_FAMILY, 12, "bold"), fg_color=STONE200, hover_color=STONE100, text_color=STONE600, height=40, corner_radius=10, command=self.toggle_live)
        self.live_btn.pack(side="left")

        # Live stats bar (always visible)
        self.stats_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_bar.pack(fill="x", padx=32, pady=(0,8))
        self.stats_bar.columnconfigure((0,1,2,3,4), weight=1)
        self._stat_widgets = {}
        stat_defs = [("cpu", "CPU", "0%", BLUE), ("mem", "Memory", "0%", "#a855f7"),
                     ("procs", "Processes", "0", GREEN), ("threads", "Threads", "0", AMBER),
                     ("uptime", "Refresh", "—", STONE500)]
        for i, (key, label, val, color) in enumerate(stat_defs):
            c = Card(self.stats_bar)
            c.grid(row=0, column=i, padx=3, sticky="nsew")
            ctk.CTkLabel(c, text=label, font=(FONT_FAMILY, 10), text_color=STONE400).pack(padx=10, pady=(10,2), anchor="w")
            lbl = ctk.CTkLabel(c, text=val, font=(FONT_FAMILY, 18, "bold"), text_color=color)
            lbl.pack(padx=10, pady=(0,10), anchor="e")
            self._stat_widgets[key] = lbl

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=32, pady=(0,32))

        # Initial stats update
        self._update_stats_bar()
        # Start background stats refresh
        self._schedule_stats_refresh()

    def destroy(self):
        self._alive = False
        self._auto_refresh = False
        super().destroy()

    def _schedule_stats_refresh(self):
        if not self._alive: return
        try:
            self.after(3000, self._refresh_stats_tick)
        except: pass

    def _refresh_stats_tick(self):
        if not self._alive: return
        self._update_stats_bar()
        if self._auto_refresh:
            self._do_live_refresh()
        self._schedule_stats_refresh()

    def _update_stats_bar(self):
        try:
            cpu = psutil.cpu_percent(interval=0)
            mem = psutil.virtual_memory()
            proc_count = len(list(psutil.process_iter()))
            thread_count = 0
            for p in psutil.process_iter(['num_threads']):
                try: thread_count += p.info['num_threads'] or 0
                except: pass
            self._stat_widgets['cpu'].configure(text=f"{cpu:.1f}%")
            self._stat_widgets['mem'].configure(text=f"{mem.percent:.1f}%")
            self._stat_widgets['procs'].configure(text=str(proc_count))
            self._stat_widgets['threads'].configure(text=str(thread_count))
            import datetime
            self._stat_widgets['uptime'].configure(text=datetime.datetime.now().strftime("%H:%M:%S"))
        except: pass

    def toggle_live(self):
        self._auto_refresh = not self._auto_refresh
        if self._auto_refresh:
            self.live_btn.configure(text="🟢 Live Mode: ON", fg_color=GREEN, hover_color="#059669", text_color=WHITE)
            self.scan_processes()
        else:
            self.live_btn.configure(text="🔴 Live Mode: OFF", fg_color=STONE200, hover_color=STONE100, text_color=STONE600)

    def _do_live_refresh(self):
        """Called periodically when live mode is on — refresh process table in-place."""
        try:
            self.scan_processes()
        except: pass

    def scan_processes(self):
        for w in self.content.winfo_children(): w.destroy()
        procs = []
        for proc in psutil.process_iter(['pid','name','status','cpu_percent','memory_info','num_threads']):
            try:
                info = proc.info
                mem = info['memory_info'].rss/(1024*1024) if info['memory_info'] else 0
                procs.append({'pid':info['pid'],'name':info['name'] or 'Unknown','status':info['status'] or 'unknown',
                              'cpu':info['cpu_percent'] or 0,'mem':round(mem,1),'threads':info['num_threads'] or 0})
            except: continue
        procs.sort(key=lambda x: x['mem'], reverse=True)

        # Summary
        total_mem = sum(p['mem'] for p in procs)
        running = sum(1 for p in procs if p['status']=='running')
        summary = Card(self.content)
        summary.pack(fill="x", pady=(0,8))
        sf = ctk.CTkFrame(summary, fg_color="transparent")
        sf.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(sf, text=f"Total: {len(procs)} processes", font=(FONT_FAMILY, 12, "bold"), text_color=STONE800).pack(side="left", padx=(0,16))
        ctk.CTkLabel(sf, text=f"Running: {running}", font=(FONT_FAMILY, 12), text_color=GREEN).pack(side="left", padx=(0,16))
        ctk.CTkLabel(sf, text=f"Memory: {total_mem:.0f} MB", font=(FONT_FAMILY, 12), text_color=STONE500).pack(side="left", padx=(0,16))
        ctk.CTkLabel(sf, text=f"Threads: {sum(p['threads'] for p in procs)}", font=(FONT_FAMILY, 12), text_color=STONE500).pack(side="left")
        if self._auto_refresh:
            ctk.CTkFrame(sf, width=8, height=8, corner_radius=4, fg_color=GREEN).pack(side="right", padx=(0,4))
            ctk.CTkLabel(sf, text="LIVE", font=(FONT_FAMILY, 9, "bold"), text_color=GREEN).pack(side="right")

        # Table
        table_card = Card(self.content)
        table_card.pack(fill="x")
        table = ctk.CTkFrame(table_card, fg_color="transparent")
        table.pack(fill="x", padx=16, pady=16)
        headers = ['PID','Name','Status','CPU %','Memory (MB)','Threads']
        widths = [60,200,80,60,90,60]
        for j, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(table, text=h, font=(FONT_FAMILY, 10, "bold"), text_color=STONE400, width=w).grid(row=0, column=j, padx=2, pady=4)
        for i, p in enumerate(procs[:50]):
            sc = GREEN if p['status']=='running' else AMBER if p['status']=='sleeping' else RED
            vals = [str(p['pid']), p['name'][:25], p['status'], f"{p['cpu']:.1f}", f"{p['mem']:.1f}", str(p['threads'])]
            colors = [AMBER, STONE800, sc, STONE700, STONE700, STONE700]
            for j, (v, c, w) in enumerate(zip(vals, colors, widths)):
                ctk.CTkLabel(table, text=v, font=(FONT_FAMILY, 10), text_color=c, width=w, anchor="w").grid(row=i+1, column=j, padx=2, pady=1)

    def detect_deadlocks(self):
        for w in self.content.winfo_children(): w.destroy()
        ctk.CTkLabel(self.content, text="Analyzing process dependencies...", font=(FONT_FAMILY, 12), text_color=STONE500).pack(pady=8)
        import os
        nodes, edges, shared_files = [], [], {}
        process_files, pid_name = {}, {}
        for proc in psutil.process_iter(['pid','name']):
            try:
                info = proc.info
                pid, name = info['pid'], info['name'] or 'Unknown'
                pid_name[pid] = name
                files = set()
                try:
                    for f in proc.open_files(): files.add(f.path)
                except: pass
                if files: process_files[pid] = files
            except: continue

        file_holders = {}
        for pid, files in process_files.items():
            for f in files:
                file_holders.setdefault(f, []).append(pid)
        shared_files = {f:h for f,h in file_holders.items() if len(h)>=2}

        resource_set = set()
        for fp, holders in list(shared_files.items())[:15]:
            r_id = f"R:{os.path.basename(fp)[:20]}"
            if r_id not in resource_set:
                nodes.append({'id':r_id,'type':'resource'})
                resource_set.add(r_id)
            for i, pid in enumerate(holders):
                p_id = f"P:{pid}"
                if not any(n['id']==p_id for n in nodes):
                    nodes.append({'id':p_id,'type':'process'})
                if i==0: edges.append({'source':r_id,'target':p_id})
                else: edges.append({'source':p_id,'target':r_id})

        for w in self.content.winfo_children(): w.destroy()
        if not nodes:
            rc = ctk.CTkFrame(self.content, fg_color=GREEN_LIGHT, corner_radius=12, border_width=1, border_color="#a7f3d0")
            rc.pack(fill="x")
            ctk.CTkLabel(rc, text="🟢 No Resource Contention Found", font=(FONT_FAMILY, 15, "bold"), text_color="#047857").pack(padx=16, pady=(16,4))
            ctk.CTkLabel(rc, text="No processes are sharing resources. System is free from deadlocks.", font=(FONT_FAMILY, 11), text_color=STONE600).pack(padx=16, pady=(0,16))
            return

        ctk.CTkLabel(self.content, text=f"Found {len(shared_files)} shared resources across {len(nodes)} nodes", font=(FONT_FAMILY, 12), text_color=GREEN).pack(pady=(0,8), anchor="w")
        dl, procs_inv, cycle = detect_deadlock(nodes, edges)
        if dl:
            rc = ctk.CTkFrame(self.content, fg_color=RED_LIGHT, corner_radius=12, border_width=1, border_color="#fecaca")
            rc.pack(fill="x")
            ctk.CTkLabel(rc, text="🔴 Potential Deadlock Detected!", font=(FONT_FAMILY, 15, "bold"), text_color="#b91c1c").pack(padx=16, pady=(16,4))
            ctk.CTkLabel(rc, text=f"Cycle: {' → '.join(cycle)}", font=(FONT_FAMILY, 11), text_color=STONE700, wraplength=600).pack(padx=16, pady=(0,16))
        else:
            rc = ctk.CTkFrame(self.content, fg_color=GREEN_LIGHT, corner_radius=12, border_width=1, border_color="#a7f3d0")
            rc.pack(fill="x")
            ctk.CTkLabel(rc, text="🟢 No Deadlock Detected", font=(FONT_FAMILY, 15, "bold"), text_color="#047857").pack(padx=16, pady=(16,4))
            ctk.CTkLabel(rc, text="Shared resources exist but no circular dependency found.", font=(FONT_FAMILY, 11), text_color=STONE600).pack(padx=16, pady=(0,16))

        # Shared resources table
        if shared_files:
            import os
            table_card = Card(self.content)
            table_card.pack(fill="x", pady=(8,0))
            ctk.CTkLabel(table_card, text="Shared Resources (Contention Points)", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
            for fp, holders in list(shared_files.items())[:10]:
                f = ctk.CTkFrame(table_card, fg_color=STONE50, corner_radius=6)
                f.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(f, text=os.path.basename(fp)[:40], font=(FONT_FAMILY, 10, "bold"), text_color=GREEN).pack(side="left", padx=8, pady=4)
                names = [f"{pid_name.get(p,'?')}({p})" for p in holders[:3]]
                ctk.CTkLabel(f, text=", ".join(names), font=(FONT_FAMILY, 10), text_color=STONE500).pack(side="left", padx=4)
            ctk.CTkLabel(table_card, text="", font=(FONT_FAMILY, 1)).pack(pady=8)

    def start_live_overview(self):
        """Start the live system overview with auto-refresh."""
        self._overview_active = True
        self._render_overview()

    def _render_overview(self):
        if not self._alive: return
        for w in self.content.winfo_children(): w.destroy()
        cpu = psutil.cpu_percent(interval=0)
        mem = psutil.virtual_memory()
        try:
            disk = psutil.disk_usage('/')
        except:
            disk = psutil.disk_usage('C:\\')
        cpu_count = psutil.cpu_count()

        # Live indicator
        live_hdr = ctk.CTkFrame(self.content, fg_color="transparent")
        live_hdr.pack(fill="x", pady=(0,8))
        ctk.CTkFrame(live_hdr, width=8, height=8, corner_radius=4, fg_color=GREEN).pack(side="left", padx=(0,6))
        ctk.CTkLabel(live_hdr, text="LIVE — Auto-refreshing every 3s", font=(FONT_FAMILY, 10, "bold"), text_color=GREEN).pack(side="left")
        import datetime
        ctk.CTkLabel(live_hdr, text=datetime.datetime.now().strftime("%H:%M:%S"), font=(FONT_FAMILY, 10), text_color=STONE400).pack(side="right")

        stats_f = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_f.pack(fill="x", pady=(0,12))
        stats_f.columnconfigure((0,1,2), weight=1)

        for i, (label, pct, used, total, color) in enumerate([
            ("CPU", cpu, f"{cpu_count} cores", "100%", BLUE),
            ("Memory", mem.percent, f"{mem.used/(1024**3):.1f} GB", f"{mem.total/(1024**3):.1f} GB", "#a855f7"),
            ("Disk", disk.percent, f"{disk.used/(1024**3):.1f} GB", f"{disk.total/(1024**3):.1f} GB", AMBER),
        ]):
            c = Card(stats_f)
            c.grid(row=0, column=i, padx=4, sticky="nsew")
            ctk.CTkLabel(c, text=label, font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,4), anchor="w")
            ctk.CTkLabel(c, text=f"{pct:.1f}%", font=(FONT_FAMILY, 28, "bold"), text_color=color).pack(padx=16, anchor="w")
            bar_bg = ctk.CTkFrame(c, fg_color=STONE200, height=8, corner_radius=4)
            bar_bg.pack(fill="x", padx=16, pady=(4,4))
            bar_bg.pack_propagate(False)
            fill_w = max(1, int(pct * 1.8))
            ctk.CTkFrame(bar_bg, fg_color=color, height=8, corner_radius=4, width=fill_w).pack(side="left")
            ctk.CTkLabel(c, text=f"{used} / {total}", font=(FONT_FAMILY, 10), text_color=STONE500).pack(padx=16, pady=(0,16), anchor="w")

        # Process status breakdown
        statuses = {}
        for p in psutil.process_iter():
            try:
                s = p.status()
                statuses[s] = statuses.get(s,0)+1
            except: pass
        status_card = Card(self.content)
        status_card.pack(fill="x", pady=(8,0))
        ctk.CTkLabel(status_card, text="Process Status Breakdown", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800).pack(padx=16, pady=(16,8), anchor="w")
        sf = ctk.CTkFrame(status_card, fg_color="transparent")
        sf.pack(fill="x", padx=16, pady=(0,16))
        colors_map = {'running': GREEN, 'sleeping': BLUE, 'disk-sleep': AMBER, 'stopped': RED, 'zombie': RED}
        for s, cnt in sorted(statuses.items(), key=lambda x: x[1], reverse=True)[:6]:
            sc = colors_map.get(s, STONE500)
            chip = ctk.CTkFrame(sf, fg_color=STONE50, corner_radius=6)
            chip.pack(side="left", padx=2)
            ctk.CTkFrame(chip, width=6, height=6, corner_radius=3, fg_color=sc).pack(side="left", padx=(8,4), pady=6)
            ctk.CTkLabel(chip, text=f"{s}: {cnt}", font=(FONT_FAMILY, 11), text_color=STONE600).pack(side="left", padx=(0,8), pady=4)

        # Schedule next refresh
        if hasattr(self, '_overview_active') and self._overview_active:
            try:
                self.after(3000, self._render_overview)
            except:
                pass
# ══════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════

class DeadlockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Deadlock Prevention & Recovery Toolkit")
        self.geometry("1280x800")
        self.minsize(1000, 600)
        self.configure(fg_color=STONE50)
        self.system = None
        self.current_page = None
        self.pages = {}
        self.nav_buttons = {}

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=WHITE, corner_radius=0, border_width=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar header
        hdr = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(20,24))
        ctk.CTkLabel(hdr, text="Deadlock Prevention &\nRecovery Toolkit", font=(FONT_FAMILY, 13, "bold"), text_color=STONE800, justify="left").pack(anchor="w")

        # Nav items
        nav_items = [
            ("setup",      "⚙  System Setup",      SetupPage),
            ("bankers",    "🏦  Banker's Algorithm", BankersPage),
            ("detection",  "🔍  Deadlock Detection", DetectionPage),
            ("recovery",   "🔧  Recovery",           RecoveryPage),
            ("simulation", "⚡  Simulation",          SimulationPage),
            ("rag",        "📊  RAG Visualizer",     RAGVisualizerPage),
            ("monitor",    "🖥  Process Monitor",    ProcessMonitorPage),
        ]
        for key, label, page_cls in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, font=(FONT_FAMILY, 12),
                fg_color="transparent", hover_color=ORANGE_LIGHT,
                text_color=STONE600, height=38, corner_radius=8, anchor="w",
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x", padx=8, pady=1)
            self.nav_buttons[key] = (btn, page_cls)

        # System status at bottom
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        status_f = ctk.CTkFrame(self.sidebar, fg_color=STONE50, corner_radius=8)
        status_f.pack(fill="x", padx=12, pady=(0,16))
        ctk.CTkLabel(status_f, text="SYSTEM STATUS", font=(FONT_FAMILY, 9, "bold"), text_color=STONE400).pack(padx=12, pady=(8,2), anchor="w")
        sf = ctk.CTkFrame(status_f, fg_color="transparent")
        sf.pack(fill="x", padx=12, pady=(0,8))
        ctk.CTkFrame(sf, width=8, height=8, corner_radius=4, fg_color=GREEN).pack(side="left", padx=(0,6))
        ctk.CTkLabel(sf, text="Engine Ready", font=(FONT_FAMILY, 11), text_color=GREEN).pack(side="left")

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=STONE50, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self.show_page("setup")

    def show_page(self, key):
        # Update sidebar highlighting
        for k, (btn, _) in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=ORANGE_LIGHT, text_color=ORANGE)
            else:
                btn.configure(fg_color="transparent", text_color=STONE600)

        # Destroy current page
        for w in self.content.winfo_children():
            w.destroy()

        # Create new page
        _, page_cls = self.nav_buttons[key]
        page = page_cls(self.content, self)
        page.pack(fill="both", expand=True)
        self.current_page = page


# ══════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════

if __name__ == "__main__":
    app = DeadlockApp()
    app.mainloop()

