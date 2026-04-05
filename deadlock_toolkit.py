#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           DEADLOCK PREVENTION & DETECTION TOOLKIT           ║
║                    Terminal UI Edition                       ║
╚══════════════════════════════════════════════════════════════╝

A comprehensive toolkit for understanding and demonstrating
deadlock concepts in Operating Systems:
  1. Banker's Algorithm    (Prevention / Safety Check)
  2. Deadlock Detection    (Cycle Detection in RAG)
  3. Deadlock Recovery     (Terminate / Preemption Strategies)
  4. Simulation Engine     (Step-by-step Scenario Simulation)

Run:  python deadlock_toolkit.py
"""

import os
import random
import time
import sys
import itertools
import threading
import psutil

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich import box
from rich.align import Align
from rich.tree import Tree
from rich.live import Live
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.spinner import Spinner
from rich.progress_bar import ProgressBar

console = Console()

# ─────────────────────────────────────────────────────────────
# ANIMATION HELPERS
# ─────────────────────────────────────────────────────────────

ANIM_COLORS = ["bright_cyan", "bright_blue", "bright_magenta", "bright_green", "bright_yellow"]

def typing_effect(text, style="white", speed=0.02):
    """Print text character-by-character with a typewriter effect."""
    for char in text:
        console.print(f"[{style}]{char}[/]", end="")
        time.sleep(speed)
    console.print()

def animated_spinner(message, duration=1.5):
    """Show a Rich spinner for a given duration."""
    with Progress(
        SpinnerColumn("dots12", style="bright_cyan"),
        TextColumn(f"[bold bright_cyan]{message}[/]"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=100)
        elapsed = 0
        while elapsed < duration:
            step = min(5, 100 - progress.tasks[0].completed)
            progress.advance(task, step)
            time.sleep(0.05)
            elapsed += 0.05

def progress_animation(task_name, steps=20, duration=1.0):
    """Animated progress bar that fills step-by-step."""
    with Progress(
        TextColumn(f"  [bold bright_cyan]{task_name}[/]"),
        BarColumn(bar_width=40, style="dim", complete_style="bright_cyan", finished_style="bright_green"),
        TextColumn("[bold]{task.percentage:>3.0f}%[/]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=steps)
        for _ in range(steps):
            progress.advance(task, 1)
            time.sleep(duration / steps)

def fade_in_panel(panel, delay=0.04):
    """Simulate a fade-in by printing a panel line-by-line."""
    rendered = console.render_str(panel) if isinstance(panel, str) else None
    # Render using console capture
    with console.capture() as cap:
        console.print(panel)
    lines = cap.get().split("\n")
    for line in lines:
        console.print(line, highlight=False)
        time.sleep(delay)

def transition_screen(title=""):
    """Clear screen with a brief wipe-transition animation."""
    width = console.width
    wipe_chars = ["░", "▒", "▓", "█"]
    for ch in wipe_chars:
        line = ch * width
        console.print(f"[dim bright_cyan]{line}[/]", end="\r")
        time.sleep(0.04)
    clear_screen()
    if title:
        console.print()

def reveal_text_lines(lines, style="white", delay=0.06):
    """Reveal a list of text lines one-by-one with a cascade effect."""
    for line in lines:
        console.print(f"[{style}]{line}[/]")
        time.sleep(delay)

def pulse_result(text, style="bold bright_green", pulses=3):
    """Pulse/blink a result message."""
    for i in range(pulses):
        console.print(f"\r[{style}]{text}[/]", end="")
        time.sleep(0.25)
        console.print(f"\r[dim]{text}[/]", end="")
        time.sleep(0.15)
    console.print(f"\r[{style}]{text}[/]")

# ─────────────────────────────────────────────────────────────
# DYNAMIC DATA GENERATORS
# ─────────────────────────────────────────────────────────────

def generate_random_bankers_data(n=None, m=None):
    """Generate a valid random Banker's Algorithm scenario."""
    if n is None:
        n = random.randint(3, 6)
    if m is None:
        m = random.randint(2, 4)

    processes = [f"P{i}" for i in range(n)]
    resources = [chr(65 + i) for i in range(m)]

    total = [random.randint(5, 12) for _ in range(m)]
    allocation = [[0] * m for _ in range(n)]
    max_matrix = [[0] * m for _ in range(n)]

    # Distribute some resources to processes
    for j in range(m):
        remaining = total[j]
        for i in range(n):
            alloc = random.randint(0, min(remaining, total[j] // n + 2))
            allocation[i][j] = alloc
            remaining -= alloc
            max_matrix[i][j] = allocation[i][j] + random.randint(0, min(remaining + 2, total[j] - allocation[i][j]))

    available = [total[j] - sum(allocation[i][j] for i in range(n)) for j in range(m)]
    # Ensure available is non-negative
    for j in range(m):
        if available[j] < 0:
            available[j] = 0

    return processes, resources, allocation, max_matrix, available

def generate_random_rag(deadlock=None):
    """Generate a random Resource Allocation Graph, optionally forcing deadlock."""
    num_procs = random.randint(2, 5)
    num_res = random.randint(2, 4)

    nodes = [{'id': f'P{i+1}', 'type': 'process'} for i in range(num_procs)]
    nodes += [{'id': f'R{i+1}', 'type': 'resource'} for i in range(num_res)]

    edges = []

    if deadlock is None:
        deadlock = random.choice([True, False])

    if deadlock and num_procs >= 2 and num_res >= 2:
        # Create a guaranteed cycle: P1->R1->P2->R2->P1
        cycle_len = min(num_procs, num_res)
        for i in range(cycle_len):
            p = f'P{i+1}'
            r = f'R{i+1}'
            next_p = f'P{(i+1) % cycle_len + 1}'
            edges.append({'source': p, 'target': r})  # P requests R
            edges.append({'source': r, 'target': next_p})  # R assigned to next P
        # Add a few extra random edges
        for _ in range(random.randint(0, 3)):
            p = f'P{random.randint(1, num_procs)}'
            r = f'R{random.randint(1, num_res)}'
            edges.append({'source': p, 'target': r})
    else:
        # Random edges, no guaranteed cycle
        for _ in range(random.randint(2, num_procs + num_res)):
            if random.random() < 0.5:
                src = f'P{random.randint(1, num_procs)}'
                tgt = f'R{random.randint(1, num_res)}'
            else:
                src = f'R{random.randint(1, num_res)}'
                tgt = f'P{random.randint(1, num_procs)}'
            edges.append({'source': src, 'target': tgt})

    return nodes, edges

def generate_random_recovery_data():
    """Generate a random deadlocked scenario for recovery."""
    num_procs = random.randint(2, 4)
    num_resources = random.randint(2, 3)
    deadlocked = [f'P{i}' for i in range(num_procs)]
    resource_labels = [chr(65 + i) for i in range(num_resources)]
    allocation = [[random.randint(1, 4) for _ in range(num_resources)] for _ in range(num_procs)]
    available = [random.randint(0, 2) for _ in range(num_resources)]
    return deadlocked, resource_labels, allocation, available, num_resources


# ─────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def press_enter():
    console.print()
    console.input("[dim italic]  ⏎  Press Enter to continue...[/]")


def with_repeat(func, name):
    """Run a feature, then offer Run Again / Exit to Main Menu."""
    while True:
        func()
        console.print()
        console.print(Rule("", style="dim"))
        console.print(f"\n  [cyan]1.[/] [bold]🔄 Run {name} Again[/]")
        console.print(f"  [cyan]2.[/] [bold]🚪 Exit to Main Menu[/]")
        action = console.input("\n[bold cyan]  Your choice (1-2): [/]").strip()
        if action != '1':
            return

def get_int(prompt, min_val=1, max_val=99):
    while True:
        try:
            val = int(console.input(f"[cyan]  {prompt}[/] "))
            if min_val <= val <= max_val:
                return val
            console.print(f"[red]  Please enter a value between {min_val} and {max_val}.[/]")
        except (ValueError, EOFError):
            console.print("[red]  Invalid input. Please enter a number.[/]")

def get_matrix(rows, cols, name):
    console.print(f"\n[bold yellow]  Enter {name} (row by row, space-separated):[/]")
    matrix = []
    for i in range(rows):
        while True:
            try:
                line = console.input(f"[cyan]    Row {i} (P{i}):[/] ")
                values = list(map(int, line.split()))
                if len(values) == cols:
                    matrix.append(values)
                    break
                console.print(f"[red]    Expected {cols} values, got {len(values)}. Try again.[/]")
            except (ValueError, EOFError):
                console.print("[red]    Invalid input. Enter space-separated integers.[/]")
    return matrix

def get_vector(length, name):
    while True:
        try:
            line = console.input(f"[cyan]  {name} (space-separated):[/] ")
            values = list(map(int, line.split()))
            if len(values) == length:
                return values
            console.print(f"[red]  Expected {length} values, got {len(values)}. Try again.[/]")
        except (ValueError, EOFError):
            console.print("[red]  Invalid input. Enter space-separated integers.[/]")


def render_matrix_table(matrix, processes, resources, title, color="cyan"):
    table = Table(title=title, box=box.ROUNDED, border_style=color, show_lines=True)
    table.add_column("Process", style="bold magenta", justify="center")
    for r in resources:
        table.add_column(r, style="white", justify="center")
    for i, p in enumerate(processes):
        row = [str(matrix[i][j]) for j in range(len(resources))]
        table.add_row(p, *row)
    return table

def render_vector_table(vector, resources, title, color="yellow"):
    table = Table(title=title, box=box.ROUNDED, border_style=color)
    for r in resources:
        table.add_column(r, style="white", justify="center")
    table.add_row(*[str(v) for v in vector])
    return table


# ─────────────────────────────────────────────────────────────
# ALGORITHM 1: BANKER'S ALGORITHM
# ─────────────────────────────────────────────────────────────

def bankers_safety_check(processes, resources, allocation, max_matrix, available):
    """Banker's Algorithm — returns (safe, safe_sequence, need_matrix, log)"""
    n = len(processes)
    m = len(resources)

    need = [[max_matrix[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False] * n
    safe_sequence = []
    log = []

    log.append(f"Initial Work: {work}")

    count = 0
    while count < n:
        found = False
        for i in range(n):
            if not finish[i]:
                if all(need[i][j] <= work[j] for j in range(m)):
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


def run_bankers():
    transition_screen()
    console.print(Panel(
        "[bold white]🏦 BANKER'S ALGORITHM[/]\n[dim]Deadlock Prevention through Safety State Analysis[/]",
        border_style="bright_cyan", box=box.DOUBLE_EDGE, padding=(1, 4)
    ))

    # Choose data source
    console.print("\n[bold]  Choose data input mode:[/]\n")
    console.print("  [cyan]1.[/] [bold]🎲 Generate Random Scenario[/]")
    console.print("     [dim]Auto-generate a valid random system state[/]")
    console.print("  [cyan]2.[/] [bold]✏️  Enter Data Manually[/]")
    console.print("     [dim]Specify matrices and vectors yourself[/]")

    mode = console.input("\n[cyan]  Your choice (1-2):[/] ").strip()

    if mode == '1':
        animated_spinner("Generating random system scenario...", duration=1.2)
        processes, resources, allocation, max_matrix, available = generate_random_bankers_data()
        n, m = len(processes), len(resources)
        console.print(f"\n  [green]✓[/] Generated scenario: [bold]{n} processes[/], [bold]{m} resource types[/]")
    else:
        n = get_int("Number of Processes (2-10):", 2, 10)
        m = get_int("Number of Resource Types (1-8):", 1, 8)
        processes = [f"P{i}" for i in range(n)]
        resources = [chr(65 + i) for i in range(m)]
        console.print(f"\n  Processes: [bold]{', '.join(processes)}[/]")
        console.print(f"  Resources: [bold]{', '.join(resources)}[/]\n")
        allocation = get_matrix(n, m, "Allocation Matrix")
        max_matrix = get_matrix(n, m, "Max Matrix")
        available = get_vector(m, "Available Resources")

    # Show input tables with reveal
    console.print()
    console.print(Columns([
        render_matrix_table(allocation, processes, resources, "📊 Allocation", "cyan"),
        render_matrix_table(max_matrix, processes, resources, "📊 Max", "blue"),
    ], padding=2))
    time.sleep(0.3)

    console.print()
    console.print(render_vector_table(available, resources, "📦 Available", "yellow"))

    # Run algorithm with animated progress
    console.print()
    console.print(Rule("[bold]Running Safety Check[/]", style="bright_cyan"))
    progress_animation("Analyzing system safety", steps=25, duration=1.5)

    safe, sequence, need, log = bankers_safety_check(processes, resources, allocation, max_matrix, available)

    # Show Need Matrix
    console.print()
    console.print(render_matrix_table(need, processes, resources, "📋 Need Matrix (Max - Allocation)", "magenta"))

    # Show execution log with typing animation
    console.print()
    log_panel_lines = []
    for i, line in enumerate(log):
        if "UNSAFE" in line:
            log_panel_lines.append(f"[red]  [{i+1}] {line}[/]")
        elif "SAFE" in line:
            log_panel_lines.append(f"[green]  [{i+1}] {line}[/]")
        elif "finished" in line:
            log_panel_lines.append(f"[bright_green]  [{i+1}] {line}[/]")
        elif "can be" in line:
            log_panel_lines.append(f"[yellow]  [{i+1}] {line}[/]")
        else:
            log_panel_lines.append(f"[dim]  [{i+1}] {line}[/]")

    # Reveal log lines one-by-one
    console.print(Panel.fit("[bold]Execution Log[/]", border_style="bright_black", box=box.ROUNDED))
    for log_line in log_panel_lines:
        console.print(f"  {log_line}")
        time.sleep(0.12)

    # Final result with pulse
    console.print()
    if safe:
        seq_str = " → ".join(sequence)
        pulse_result("  ✅ SYSTEM IS SAFE", style="bold bright_green", pulses=3)
        result_panel = Panel(
            f"[bold bright_green]✅ SYSTEM IS SAFE[/]\n\n"
            f"[white]Safe Sequence:[/] [bold bright_cyan]{seq_str}[/]",
            border_style="green", box=box.DOUBLE_EDGE, padding=(1, 4)
        )
    else:
        pulse_result("  ❌ SYSTEM IS UNSAFE", style="bold bright_red", pulses=3)
        result_panel = Panel(
            "[bold bright_red]❌ SYSTEM IS UNSAFE[/]\n\n"
            "[white]No safe sequence exists. The system may deadlock.[/]",
            border_style="red", box=box.DOUBLE_EDGE, padding=(1, 4)
        )
    fade_in_panel(result_panel, delay=0.05)

    press_enter()


# ─────────────────────────────────────────────────────────────
# ALGORITHM 2: DEADLOCK DETECTION (DFS Cycle Detection in RAG)
# ─────────────────────────────────────────────────────────────

def detect_deadlock(nodes, edges):
    """DFS-based cycle detection in Resource Allocation Graph."""
    adj = {n['id']: [] for n in nodes}
    for e in edges:
        adj[e['source']].append(e['target'])

    visited = set()
    rec_stack = set()
    cycle_path = []

    def find_cycle(u, path):
        nonlocal cycle_path
        visited.add(u)
        rec_stack.add(u)
        path.append(u)
        for v in adj[u]:
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

    deadlock = False
    for node in nodes:
        if node['id'] not in visited:
            if find_cycle(node['id'], []):
                deadlock = True
                break

    processes_involved = [nid for nid in cycle_path if any(n['id'] == nid and n['type'] == 'process' for n in nodes)]

    return deadlock, processes_involved, cycle_path


PRESETS = {
    '1': {
        'name': 'Deadlock Scenario',
        'nodes': [
            {'id': 'P1', 'type': 'process'}, {'id': 'P2', 'type': 'process'}, {'id': 'P3', 'type': 'process'},
            {'id': 'R1', 'type': 'resource'}, {'id': 'R2', 'type': 'resource'},
        ],
        'edges': [
            {'source': 'P1', 'target': 'R1'}, {'source': 'R1', 'target': 'P2'},
            {'source': 'P2', 'target': 'R2'}, {'source': 'R2', 'target': 'P1'},
            {'source': 'P3', 'target': 'R2'},
        ],
    },
    '2': {
        'name': 'Safe Scenario (No Deadlock)',
        'nodes': [
            {'id': 'P1', 'type': 'process'}, {'id': 'P2', 'type': 'process'},
            {'id': 'R1', 'type': 'resource'}, {'id': 'R2', 'type': 'resource'},
        ],
        'edges': [
            {'source': 'P1', 'target': 'R1'}, {'source': 'R2', 'target': 'P2'},
        ],
    },
    '3': {
        'name': 'Complex Deadlock (3 Process Cycle)',
        'nodes': [
            {'id': 'P1', 'type': 'process'}, {'id': 'P2', 'type': 'process'}, {'id': 'P3', 'type': 'process'},
            {'id': 'R1', 'type': 'resource'}, {'id': 'R2', 'type': 'resource'}, {'id': 'R3', 'type': 'resource'},
        ],
        'edges': [
            {'source': 'P1', 'target': 'R1'}, {'source': 'R1', 'target': 'P2'},
            {'source': 'P2', 'target': 'R2'}, {'source': 'R2', 'target': 'P3'},
            {'source': 'P3', 'target': 'R3'}, {'source': 'R3', 'target': 'P1'},
        ],
    },
}


def render_rag_ascii(nodes, edges, cycle_path=None):
    """Render a simple ASCII representation of the Resource Allocation Graph."""
    if cycle_path is None:
        cycle_path = []
    cycle_set = set()
    for i in range(len(cycle_path)):
        cycle_set.add((cycle_path[i], cycle_path[(i + 1) % len(cycle_path)]))

    lines = []
    lines.append("[bold]Resource Allocation Graph:[/]\n")
    
    procs = [n for n in nodes if n['type'] == 'process']
    ress = [n for n in nodes if n['type'] == 'resource']
    
    lines.append("  [bold blue]Processes:[/] " + "  ".join(f"[bold cyan]⬡ {p['id']}[/]" for p in procs))
    lines.append("  [bold green]Resources:[/] " + "  ".join(f"[bold green]■ {r['id']}[/]" for r in ress))
    lines.append("")
    lines.append("  [bold]Edges:[/]")
    
    for e in edges:
        src, tgt = e['source'], e['target']
        in_cycle = (src, tgt) in cycle_set
        
        src_type = next((n['type'] for n in nodes if n['id'] == src), 'process')
        tgt_type = next((n['type'] for n in nodes if n['id'] == tgt), 'process')
        
        if src_type == 'process':
            label = "requests"
        else:
            label = "assigned to"
        
        if in_cycle:
            lines.append(f"    [bold red]🔴 {src} ──({label})──▶ {tgt}  ← CYCLE[/]")
        else:
            lines.append(f"    [dim]   {src} ──({label})──▶ {tgt}[/]")
    
    return "\n".join(lines)


def run_detection():
    transition_screen()
    console.print(Panel(
        "[bold white]🔍 DEADLOCK DETECTION[/]\n[dim]Cycle Detection in Resource Allocation Graphs (RAG)[/]",
        border_style="bright_yellow", box=box.DOUBLE_EDGE, padding=(1, 4)
    ))

    console.print("\n[bold]  Choose an option:[/]")
    console.print("  [cyan]1.[/] Deadlock Scenario (P1,P2,P3 + R1,R2)")
    console.print("  [cyan]2.[/] Safe Scenario (No Deadlock)")
    console.print("  [cyan]3.[/] Complex Deadlock (3-Process Cycle)")
    console.print("  [cyan]4.[/] Custom Input")
    console.print("  [cyan]5.[/] [bold]🎲 Generate Random RAG[/]")
    
    choice = console.input("\n[cyan]  Your choice (1-5):[/] ").strip()

    if choice in PRESETS:
        preset = PRESETS[choice]
        nodes = preset['nodes']
        edges = preset['edges']
        console.print(f"\n  [green]Loaded preset:[/] [bold]{preset['name']}[/]")
    elif choice == '5':
        animated_spinner("Generating random Resource Allocation Graph...", duration=1.0)
        nodes, edges = generate_random_rag()
        procs = sum(1 for n in nodes if n['type'] == 'process')
        ress = sum(1 for n in nodes if n['type'] == 'resource')
        console.print(f"\n  [green]✓[/] Generated RAG: [bold]{procs} processes[/], [bold]{ress} resources[/], [bold]{len(edges)} edges[/]")
    elif choice == '4':
        nodes = []
        edges = []
        console.print("\n[yellow]  Enter nodes (type 'done' when finished):[/]")
        console.print("  [dim]Format: ID TYPE  (e.g., P1 process  or  R1 resource)[/]")
        while True:
            line = console.input("[cyan]    Node:[/] ").strip()
            if line.lower() == 'done':
                break
            parts = line.split()
            if len(parts) == 2 and parts[1] in ('process', 'resource'):
                nodes.append({'id': parts[0].upper(), 'type': parts[1]})
            else:
                console.print("[red]    Invalid. Use: ID TYPE (e.g., P1 process)[/]")

        console.print("\n[yellow]  Enter edges (type 'done' when finished):[/]")
        console.print("  [dim]Format: SOURCE TARGET  (e.g., P1 R1)[/]")
        while True:
            line = console.input("[cyan]    Edge:[/] ").strip()
            if line.lower() == 'done':
                break
            parts = line.split()
            if len(parts) == 2:
                edges.append({'source': parts[0].upper(), 'target': parts[1].upper()})
            else:
                console.print("[red]    Invalid. Use: SOURCE TARGET (e.g., P1 R1)[/]")
    else:
        console.print("[red]  Invalid choice.[/]")
        press_enter()
        return

    if not nodes:
        console.print("[red]  No nodes defined. Cannot detect deadlock.[/]")
        press_enter()
        return

    # Show the graph with animated analysis
    console.print()
    console.print(Rule("[bold]Analyzing Resource Allocation Graph[/]", style="yellow"))
    progress_animation("Scanning graph structure", steps=20, duration=1.2)

    deadlock, processes_involved, cycle_path = detect_deadlock(nodes, edges)

    # Render ASCII graph with edge-by-edge reveal
    console.print()
    console.print(Panel.fit("[bold]RAG Visualization[/]", border_style="bright_black", box=box.ROUNDED))
    
    procs = [n for n in nodes if n['type'] == 'process']
    ress = [n for n in nodes if n['type'] == 'resource']
    console.print(f"  [bold blue]Processes:[/] " + "  ".join(f"[bold cyan]⬡ {p['id']}[/]" for p in procs))
    time.sleep(0.15)
    console.print(f"  [bold green]Resources:[/] " + "  ".join(f"[bold green]■ {r['id']}[/]" for r in ress))
    time.sleep(0.15)
    console.print()
    
    cycle_set = set()
    if deadlock and cycle_path:
        for i in range(len(cycle_path)):
            cycle_set.add((cycle_path[i], cycle_path[(i + 1) % len(cycle_path)]))
    
    for e in edges:
        src, tgt = e['source'], e['target']
        in_cycle = (src, tgt) in cycle_set
        src_type = next((n['type'] for n in nodes if n['id'] == src), 'process')
        label = "requests" if src_type == 'process' else "assigned to"
        if in_cycle:
            console.print(f"    [bold red]🔴 {src} ──({label})──▶ {tgt}  ← CYCLE[/]")
        else:
            console.print(f"    [dim]   {src} ──({label})──▶ {tgt}[/]")
        time.sleep(0.15)  # Edge-by-edge reveal

    # Result with animation
    console.print()
    if deadlock:
        cycle_str = " → ".join(cycle_path) + " → " + cycle_path[0] if cycle_path else "N/A"
        proc_str = ", ".join(processes_involved) if processes_involved else "N/A"
        pulse_result("  🔴 DEADLOCK DETECTED!", style="bold bright_red", pulses=3)
        result_panel = Panel(
            f"[bold bright_red]🔴 DEADLOCK DETECTED![/]\n\n"
            f"[white]Cycle Path:[/]     [bold red]{cycle_str}[/]\n"
            f"[white]Processes:[/]      [bold red]{proc_str}[/]",
            border_style="red", box=box.DOUBLE_EDGE, padding=(1, 4)
        )
    else:
        pulse_result("  🟢 NO DEADLOCK FOUND", style="bold bright_green", pulses=3)
        result_panel = Panel(
            "[bold bright_green]🟢 NO DEADLOCK FOUND[/]\n\n"
            "[white]No cycles were found in the Resource Allocation Graph.\n"
            "The system is currently free from deadlock.[/]",
            border_style="green", box=box.DOUBLE_EDGE, padding=(1, 4)
        )
    fade_in_panel(result_panel, delay=0.05)

    press_enter()


# ─────────────────────────────────────────────────────────────
# ALGORITHM 3: DEADLOCK RECOVERY
# ─────────────────────────────────────────────────────────────

def recover_deadlock(allocation, available, deadlocked_processes, strategy):
    """Deadlock Recovery with 3 strategies."""
    steps = []
    current_alloc = [row[:] for row in allocation]
    current_avail = available[:]
    num_resources = len(available)

    if strategy == 'terminate-all':
        steps.append(f"Terminating all deadlocked processes: {', '.join(deadlocked_processes)}")
        for pid in deadlocked_processes:
            idx = int(pid.replace('P', ''))
            for j in range(num_resources):
                current_avail[j] += current_alloc[idx][j]
                current_alloc[idx][j] = 0
            steps.append(f"Process {pid} terminated. Resources released.")

    elif strategy == 'terminate-one-by-one':
        sorted_procs = sorted(deadlocked_processes,
                              key=lambda p: sum(current_alloc[int(p.replace('P', ''))]),
                              reverse=True)
        for pid in sorted_procs:
            steps.append(f"Terminating process {pid} (one-by-one strategy).")
            idx = int(pid.replace('P', ''))
            for j in range(num_resources):
                current_avail[j] += current_alloc[idx][j]
                current_alloc[idx][j] = 0
            steps.append(f"Process {pid} terminated. Available resources: {current_avail}")

    elif strategy == 'preemption':
        steps.append(f"Attempting resource preemption from: {', '.join(deadlocked_processes)}")
        remaining = list(deadlocked_processes)
        while remaining:
            remaining.sort(key=lambda p: sum(current_alloc[int(p.replace('P', ''))]))
            victim = remaining.pop(0)
            victim_idx = int(victim.replace('P', ''))
            preempted = current_alloc[victim_idx][:]
            for j in range(num_resources):
                current_avail[j] += current_alloc[victim_idx][j]
                current_alloc[victim_idx][j] = 0
            steps.append(f"Preempted resources {preempted} from {victim}. Available: {current_avail}")
            steps.append(f"Process {victim} rolled back to a safe checkpoint.")
            if remaining:
                can_proceed = all(
                    all(current_alloc[int(p.replace('P', ''))][j] <= current_avail[j] for j in range(num_resources))
                    for p in remaining
                )
                if can_proceed:
                    steps.append(f"Deadlock resolved! Remaining processes [{', '.join(remaining)}] can now proceed.")
                    break

    return strategy, steps, current_alloc


def run_recovery():
    transition_screen()
    console.print(Panel(
        "[bold white]🔧 DEADLOCK RECOVERY[/]\n[dim]Strategies to Break Cycles and Restore System Safety[/]",
        border_style="bright_magenta", box=box.DOUBLE_EDGE, padding=(1, 4)
    ))

    # Strategy Selection
    console.print("\n[bold]  Select Recovery Strategy:[/]\n")

    strategies = [
        ("1", "terminate-all",       "Terminate All",       "Stop all deadlocked processes simultaneously"),
        ("2", "terminate-one-by-one","One-by-One",          "Terminate sequentially until cycle is broken"),
        ("3", "preemption",          "Resource Preemption", "Take resources and give to other processes"),
    ]
    for num, _, name, desc in strategies:
        console.print(f"  [cyan]{num}.[/] [bold]{name}[/]")
        console.print(f"     [dim]{desc}[/]")

    s_choice = console.input("\n[cyan]  Your choice (1-3):[/] ").strip()
    if s_choice not in ('1', '2', '3'):
        console.print("[red]  Invalid choice.[/]")
        press_enter()
        return
    strategy = strategies[int(s_choice) - 1][1]
    strategy_name = strategies[int(s_choice) - 1][2]
    console.print(f"\n  [green]Selected:[/] [bold]{strategy_name}[/]\n")

    # Choose data source
    console.print("[bold]  Data input mode:[/]\n")
    console.print("  [cyan]1.[/] [bold]🎲 Generate Random Deadlock Scenario[/]")
    console.print("  [cyan]2.[/] [bold]✏️  Enter Data Manually[/]")
    data_mode = console.input("\n[cyan]  Your choice (1-2):[/] ").strip()

    if data_mode == '1':
        animated_spinner("Generating deadlock scenario...", duration=1.0)
        deadlocked, resource_labels, allocation, available, num_resources = generate_random_recovery_data()
        console.print(f"\n  [green]✓[/] Generated: [bold]{len(deadlocked)} deadlocked processes[/], [bold]{num_resources} resource types[/]")
    else:
        dp_input = console.input("[cyan]  Enter deadlocked process IDs (space-separated, e.g., P0 P1 P2):[/] ").strip()
        deadlocked = dp_input.upper().split()
        if not deadlocked:
            console.print("[red]  No processes entered.[/]")
            press_enter()
            return
        num_resources = get_int("Number of resource types (1-6):", 1, 6)
        resource_labels = [chr(65 + i) for i in range(num_resources)]
        console.print()
        allocation = get_matrix(len(deadlocked), num_resources, "Allocation Matrix (for deadlocked processes)")
        available = get_vector(num_resources, "Available Resources")

    # Need to have allocation indexed by process number
    max_idx = max(int(p.replace('P', '')) for p in deadlocked) + 1
    full_allocation = [[0] * num_resources for _ in range(max_idx)]
    for i, pid in enumerate(deadlocked):
        idx = int(pid.replace('P', ''))
        full_allocation[idx] = allocation[i]

    # Show input
    console.print()
    console.print(render_matrix_table(allocation, deadlocked, resource_labels, "📊 Allocation (Deadlocked)", "red"))
    console.print()
    console.print(render_vector_table(available, resource_labels, "📦 Available", "yellow"))

    # Run recovery with animated progress
    console.print()
    console.print(Rule(f"[bold]Executing {strategy_name}[/]", style="magenta"))
    progress_animation(f"Running {strategy_name}", steps=25, duration=1.5)

    _, steps, updated_alloc = recover_deadlock(full_allocation, available, deadlocked, strategy)

    # Show recovery steps one-by-one with animation
    console.print()
    console.print(Panel.fit("[bold]Recovery Log[/]", border_style="magenta", box=box.ROUNDED))
    for i, step in enumerate(steps):
        if "terminated" in step.lower() or "preempted" in step.lower():
            console.print(f"  [yellow]  ⚡ Step {i+1}: {step}[/]")
        elif "resolved" in step.lower() or "can now proceed" in step.lower():
            console.print(f"  [bright_green]  ✅ Step {i+1}: {step}[/]")
        else:
            console.print(f"  [white]  📌 Step {i+1}: {step}[/]")
        time.sleep(0.2)

    console.print()
    pulse_result("  ✅ RECOVERY COMPLETE", style="bold bright_green", pulses=3)
    result_panel = Panel(
        f"[bold bright_green]✅ RECOVERY COMPLETE[/]\n\n"
        f"[white]Strategy Used:[/]  [bold]{strategy_name}[/]\n"
        f"[white]System Status:[/]  [bold green]SAFE[/]",
        border_style="green", box=box.DOUBLE_EDGE, padding=(1, 4)
    )
    fade_in_panel(result_panel, delay=0.05)

    press_enter()


# ─────────────────────────────────────────────────────────────
# ALGORITHM 4: SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────

def run_simulation():
    transition_screen()
    console.print(Panel(
        "[bold white]⚡ SIMULATION ENGINE[/]\n[dim]Step-by-Step Deadlock Scenario Simulation using Banker's Algorithm[/]",
        border_style="bright_green", box=box.DOUBLE_EDGE, padding=(1, 4)
    ))

    num_processes = get_int("Number of Processes (2-10):", 2, 10)
    num_resources = get_int("Number of Resource Types (1-6):", 1, 6)

    processes = [f"P{i}" for i in range(num_processes)]
    resources = [chr(65 + i) for i in range(num_resources)]

    # Generate random system
    animated_spinner("Generating system state...", duration=0.8)
    total_resources = [random.randint(4, 11) for _ in range(num_resources)]
    allocation = [[0] * num_resources for _ in range(num_processes)]
    max_matrix = [[random.randint(0, total_resources[j]) for j in range(num_resources)] for _ in range(num_processes)]
    available = total_resources[:]

    console.print(f"\n  [bold]System Generated:[/]")
    console.print(f"  Processes: [cyan]{', '.join(processes)}[/]")
    console.print(f"  Resources: [cyan]{', '.join(resources)}[/]")
    console.print(f"  Total:     [cyan]{total_resources}[/]\n")

    # Show initial state
    console.print(render_matrix_table(max_matrix, processes, resources, "📊 Max Matrix", "blue"))
    console.print()
    console.print(render_vector_table(available, resources, "📦 Available", "yellow"))

    console.print()
    console.print(Rule("[bold]Running Live Simulation[/]", style="green"))
    console.print()

    # Simulate steps with live display
    total_steps = num_processes * 3
    logs = []

    logs.append(("info", f"Starting simulation with {num_processes} processes and {num_resources} resources."))
    logs.append(("info", f"Total Resources: {total_resources}"))
    logs.append(("info", f"Available: {available[:]}"))

    def build_live_layout(step_num, total, step_logs):
        """Build the live-updating layout for the simulation."""
        layout = Layout()
        
        # Build allocation table
        alloc_table = Table(title="📊 Current Allocation", box=box.ROUNDED, border_style="cyan", show_lines=True)
        alloc_table.add_column("Process", style="bold magenta", justify="center")
        for r in resources:
            alloc_table.add_column(r, style="white", justify="center")
        for i, p in enumerate(processes):
            row = [str(allocation[i][j]) for j in range(num_resources)]
            alloc_table.add_row(p, *row)

        # Available
        avail_str = "  ".join(f"[bold cyan]{resources[j]}[/]=[yellow]{available[j]}[/]" for j in range(num_resources))
        
        # Progress
        pct = int((step_num / total) * 100) if total > 0 else 0
        bar_filled = int(pct / 2.5)
        bar = f"[bright_green]{'█' * bar_filled}[/][dim]{'░' * (40 - bar_filled)}[/]"
        
        # Recent logs (last 6)
        recent = step_logs[-6:]
        log_text = ""
        for lt, lm in recent:
            if lt == "safe":
                log_text += f"  [green]{lm}[/]\n"
            elif lt == "denied":
                log_text += f"  [bold red]{lm}[/]\n"
            elif lt == "skip":
                log_text += f"  [dim]{lm}[/]\n"
            else:
                log_text += f"  [bright_cyan]{lm}[/]\n"

        combined = Panel(
            f"  [bold]Step:[/] [bright_cyan]{step_num}[/] / [dim]{total}[/]   {bar}  [bold]{pct}%[/]\n"
            f"  [bold]Available:[/]  {avail_str}\n\n"
            f"{log_text}",
            title="[bold]⚡ Live Simulation[/]",
            border_style="bright_green",
            box=box.DOUBLE_EDGE
        )
        return combined

    with Live(build_live_layout(0, total_steps, logs), console=console, refresh_per_second=8, transient=False) as live:
        for step in range(total_steps):
            p_idx = random.randint(0, num_processes - 1)
            r_idx = random.randint(0, num_resources - 1)
            need = max_matrix[p_idx][r_idx] - allocation[p_idx][r_idx]

            if need > 0 and available[r_idx] > 0:
                amount = min(need, available[r_idx], random.randint(1, 2))
                allocation[p_idx][r_idx] += amount
                available[r_idx] -= amount

                safe, seq, _, _ = bankers_safety_check(processes, resources, allocation, max_matrix, available)
                if safe:
                    seq_str = " → ".join(seq)
                    logs.append(("safe", f"[Step {step+1}] ✅ Granted {amount}× {resources[r_idx]} to {processes[p_idx]}. SAFE"))
                else:
                    allocation[p_idx][r_idx] -= amount
                    available[r_idx] += amount
                    logs.append(("denied", f"[Step {step+1}] ❌ Denied {amount}× {resources[r_idx]} to {processes[p_idx]}. UNSAFE"))
            else:
                logs.append(("skip", f"[Step {step+1}] ⏭  {processes[p_idx]} — no need for {resources[r_idx]}"))

            live.update(build_live_layout(step + 1, total_steps, logs))
            time.sleep(0.4)

    # Final check
    final_safe, final_seq, _, _ = bankers_safety_check(processes, resources, allocation, max_matrix, available)

    # Final summary with animation
    console.print()
    running = [p for i, p in enumerate(processes) if any(allocation[i][j] > 0 for j in range(num_resources))]
    
    stats_table = Table(box=box.SIMPLE, show_header=False, border_style="dim")
    stats_table.add_column("Stat", style="bold")
    stats_table.add_column("Value", style="cyan")
    stats_table.add_row("Running Processes", str(len(running)))
    stats_table.add_row("Blocked Processes", str(0 if final_safe else num_processes))
    stats_table.add_row("Steps Simulated", str(total_steps))
    if final_safe:
        stats_table.add_row("System Status", "[green]SAFE[/]")
        stats_table.add_row("Safe Sequence", " → ".join(final_seq))
    else:
        stats_table.add_row("System Status", "[red]UNSAFE[/]")
    
    pulse_result("  Simulation Complete!", style="bold bright_green" if final_safe else "bold bright_red", pulses=2)
    fade_in_panel(Panel(stats_table, title="[bold]Simulation Summary[/]", border_style="green" if final_safe else "red", box=box.DOUBLE_EDGE), delay=0.04)

    # Show final allocation
    console.print()
    console.print(render_matrix_table(allocation, processes, resources, "📊 Final Allocation", "cyan"))
    console.print()
    console.print(render_vector_table(available, resources, "📦 Final Available", "yellow"))

    press_enter()


# ─────────────────────────────────────────────────────────────
# FEATURE 5: LIVE PROCESS MONITOR
# ─────────────────────────────────────────────────────────────

def get_system_processes():
    """Fetch all running processes using psutil."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'num_threads']):
        try:
            info = proc.info
            mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
            procs.append({
                'pid': info['pid'],
                'name': info['name'] or 'Unknown',
                'status': info['status'] or 'unknown',
                'cpu': info['cpu_percent'] or 0.0,
                'memory_mb': round(mem_mb, 1),
                'threads': info['num_threads'] or 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return procs


def build_process_dependency_graph():
    """
    Build a Resource Allocation Graph from real system processes.
    Analyzes processes that share open files/handles to create dependencies.
    """
    nodes = []
    edges = []
    process_files = {}  # pid -> set of open file paths
    pid_name = {}       # pid -> process name

    # Collect open files for each process
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            info = proc.info
            pid = info['pid']
            name = info['name'] or 'Unknown'
            pid_name[pid] = name
            files = set()
            try:
                for f in proc.open_files():
                    files.add(f.path)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            if files:
                process_files[pid] = files
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Build dependency graph: if two processes share a file,
    # create resource nodes and edges (P->R for request, R->P for assignment)
    resource_set = set()
    pids = list(process_files.keys())

    # Track which files are held by multiple processes (contention)
    file_holders = {}  # file_path -> list of pids
    for pid, files in process_files.items():
        for f in files:
            if f not in file_holders:
                file_holders[f] = []
            file_holders[f].append(pid)

    # Only consider files shared by 2+ processes (resource contention)
    shared_files = {f: holders for f, holders in file_holders.items() if len(holders) >= 2}

    if shared_files:
        # Limit to top 15 shared resources to keep graph readable
        sorted_shared = sorted(shared_files.items(), key=lambda x: len(x[1]), reverse=True)[:15]

        for file_path, holders in sorted_shared:
            # Use short resource name
            r_name = os.path.basename(file_path)[:20] or file_path[-20:]
            r_id = f"R:{r_name}"
            if r_id not in resource_set:
                nodes.append({'id': r_id, 'type': 'resource'})
                resource_set.add(r_id)

            for i, pid in enumerate(holders):
                p_id = f"P:{pid}"
                # Add process node
                if not any(n['id'] == p_id for n in nodes):
                    nodes.append({'id': p_id, 'type': 'process'})

                if i == 0:
                    # First process "holds" the resource
                    edges.append({'source': r_id, 'target': p_id})
                else:
                    # Other processes "request" the resource
                    edges.append({'source': p_id, 'target': r_id})

    return nodes, edges, shared_files, pid_name


def run_live_monitor():
    transition_screen()
    console.print(Panel(
        "[bold white]🖥️  LIVE PROCESS MONITOR[/]\n[dim]Real-time Process Scanning & Deadlock Detection[/]",
        border_style="bright_magenta", box=box.DOUBLE_EDGE, padding=(1, 4)
    ))

    while True:
        console.print("\n[bold]  Select an option:[/]\n")
        console.print("  [cyan]1.[/] [bold]Scan Running Processes[/]")
        console.print("     [dim]View all processes on your system[/]")
        console.print("  [cyan]2.[/] [bold]Detect Deadlocks[/]")
        console.print("     [dim]Analyze process dependencies for cycles[/]")
        console.print("  [cyan]3.[/] [bold]System Overview[/]")
        console.print("     [dim]CPU, memory, and disk usage stats[/]")
        console.print("  [cyan]4.[/] [bold]Back to Main Menu[/]")

        choice = console.input("\n[cyan]  Your choice (1-4):[/] ").strip()

        if choice == '1':
            # ── Scan Running Processes ──
            transition_screen()
            console.print(Panel("[bold white]📡 SCANNING SYSTEM PROCESSES...[/]",
                                border_style="bright_cyan", box=box.ROUNDED))
            animated_spinner("Scanning system processes...", duration=1.0)

            procs = get_system_processes()

            # Optional filter
            filter_str = console.input("\n[cyan]  Filter by name (leave blank for all):[/] ").strip().lower()
            if filter_str:
                procs = [p for p in procs if filter_str in p['name'].lower()]

            # Sort by memory descending
            procs.sort(key=lambda x: x['memory_mb'], reverse=True)

            # Show table (top 50)
            table = Table(
                title=f"📊 Running Processes ({len(procs)} total, showing top 50)",
                box=box.ROUNDED, border_style="bright_cyan", show_lines=False,
            )
            table.add_column("PID", style="bold yellow", justify="right", width=8)
            table.add_column("Name", style="bold white", width=30)
            table.add_column("Status", style="dim", justify="center", width=12)
            table.add_column("CPU %", style="cyan", justify="right", width=8)
            table.add_column("Memory (MB)", style="magenta", justify="right", width=12)
            table.add_column("Threads", style="green", justify="right", width=8)

            for p in procs[:50]:
                status_color = "green" if p['status'] == 'running' else "yellow"
                table.add_row(
                    str(p['pid']),
                    p['name'][:28],
                    f"[{status_color}]{p['status']}[/]",
                    f"{p['cpu']:.1f}",
                    f"{p['memory_mb']:.1f}",
                    str(p['threads']),
                )

            console.print()
            console.print(table)

            # Summary
            total_mem = sum(p['memory_mb'] for p in procs)
            total_threads = sum(p['threads'] for p in procs)
            console.print(Panel(
                f"[bold]Total Processes:[/] [cyan]{len(procs)}[/]   │   "
                f"[bold]Total Memory:[/] [magenta]{total_mem:.0f} MB[/]   │   "
                f"[bold]Total Threads:[/] [green]{total_threads}[/]",
                border_style="dim", box=box.ROUNDED
            ))
            press_enter()

        elif choice == '2':
            # ── Detect Deadlocks ──
            transition_screen()
            console.print(Panel("[bold white]🔍 ANALYZING PROCESS DEPENDENCIES...[/]",
                                border_style="bright_yellow", box=box.ROUNDED))

            animated_spinner("Scanning open file handles across processes...", duration=1.5)

            nodes, edges, shared_files, pid_name = build_process_dependency_graph()

            if not nodes:
                console.print(Panel(
                    "[bold bright_green]🟢 NO RESOURCE CONTENTION FOUND[/]\n\n"
                    "[white]No processes are currently sharing resources.\n"
                    "The system appears free from potential deadlocks.[/]",
                    border_style="green", box=box.DOUBLE_EDGE, padding=(1, 4)
                ))
                press_enter()
                continue

            # Show shared resources info
            console.print(f"\n  [green]Found {len(shared_files)} shared resource(s) across {len(nodes)} nodes[/]")
            console.print()

            # Show dependency table
            dep_table = Table(
                title="📁 Shared Resources (Contention Points)",
                box=box.ROUNDED, border_style="yellow", show_lines=True
            )
            dep_table.add_column("Resource", style="bold green", width=35)
            dep_table.add_column("Processes Sharing", style="cyan", width=50)

            for file_path, holders in list(shared_files.items())[:15]:
                proc_names = []
                for pid in holders:
                    name = pid_name.get(pid, 'Unknown')
                    proc_names.append(f"{name} (PID:{pid})")
                dep_table.add_row(
                    os.path.basename(file_path)[:33],
                    ", ".join(proc_names[:4]) + ("..." if len(proc_names) > 4 else "")
                )

            console.print(dep_table)

            # Run deadlock detection
            console.print()
            console.print(Rule("[bold]Running DFS Cycle Detection[/]", style="yellow"))
            time.sleep(0.5)

            deadlock, processes_involved, cycle_path = detect_deadlock(nodes, edges)

            # Render RAG
            console.print()
            console.print(Panel(
                render_rag_ascii(nodes, edges, cycle_path if deadlock else None),
                title="[bold]Resource Allocation Graph (Live)[/]",
                border_style="bright_black", box=box.ROUNDED
            ))

            # Result
            console.print()
            if deadlock:
                cycle_str = " → ".join(cycle_path) + " → " + cycle_path[0] if cycle_path else "N/A"
                proc_str = ", ".join(processes_involved) if processes_involved else "N/A"
                console.print(Panel(
                    f"[bold bright_red]🔴 POTENTIAL DEADLOCK DETECTED![/]\n\n"
                    f"[white]Cycle Path:[/]     [bold red]{cycle_str}[/]\n"
                    f"[white]Processes:[/]      [bold red]{proc_str}[/]\n\n"
                    f"[dim]Note: This indicates a circular dependency in file/resource access.\n"
                    f"The involved processes may be contending for the same resources.[/]",
                    border_style="red", box=box.DOUBLE_EDGE, padding=(1, 4)
                ))
            else:
                console.print(Panel(
                    "[bold bright_green]🟢 NO DEADLOCK DETECTED[/]\n\n"
                    "[white]Although processes share resources, no circular dependency\n"
                    "(cycle) was found in the Resource Allocation Graph.\n"
                    "The system is currently free from deadlocks.[/]",
                    border_style="green", box=box.DOUBLE_EDGE, padding=(1, 4)
                ))

            press_enter()

        elif choice == '3':
            # ── Live System Overview (auto-refreshing) ──
            transition_screen()
            console.print(Panel("[bold white]🖥️  LIVE SYSTEM DASHBOARD[/]\n[dim]Auto-refreshing every 2 seconds • Press Ctrl+C to return[/]",
                                border_style="bright_green", box=box.ROUNDED))
            console.print()

            def build_system_dashboard():
                """Build a live-refreshing system dashboard."""
                cpu_percent = psutil.cpu_percent(interval=0)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                cpu_bar_filled = int(cpu_percent / 5)
                cpu_bar = f"[bright_cyan]{'█' * cpu_bar_filled}[/][dim]{'░' * (20 - cpu_bar_filled)}[/]"
                mem_bar_filled = int(mem.percent / 5)
                mem_bar = f"[magenta]{'█' * mem_bar_filled}[/][dim]{'░' * (20 - mem_bar_filled)}[/]"
                disk_bar_filled = int(disk.percent / 5)
                disk_bar = f"[yellow]{'█' * disk_bar_filled}[/][dim]{'░' * (20 - disk_bar_filled)}[/]"

                # Process stats
                proc_count = 0
                statuses = {}
                for p in psutil.process_iter():
                    try:
                        s = p.status()
                        statuses[s] = statuses.get(s, 0) + 1
                        proc_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                status_str = "  ".join(f"[dim]{k}:[/][cyan]{v}[/]" for k, v in sorted(statuses.items(), key=lambda x: x[1], reverse=True)[:5])

                import datetime
                now = datetime.datetime.now().strftime("%H:%M:%S")

                dashboard = Panel(
                    f"  [bold]⏰ Time:[/]  [bright_cyan]{now}[/]    [bold]Processes:[/]  [cyan]{proc_count}[/]\n\n"
                    f"  [bold]🔲 CPU:[/]    {cpu_bar}  [bold]{cpu_percent:>5.1f}%[/]   "
                    f"Cores: [cyan]{cpu_count}[/]" +
                    (f"   Freq: [cyan]{cpu_freq.current:.0f} MHz[/]" if cpu_freq else "") + "\n"
                    f"  [bold]💾 Memory:[/] {mem_bar}  [bold]{mem.percent:>5.1f}%[/]   "
                    f"[magenta]{mem.used / (1024**3):.1f}[/] / [dim]{mem.total / (1024**3):.1f} GB[/]   "
                    f"Free: [green]{mem.available / (1024**3):.1f} GB[/]\n"
                    f"  [bold]💿 Disk:[/]   {disk_bar}  [bold]{disk.percent:>5.1f}%[/]   "
                    f"[yellow]{disk.used / (1024**3):.1f}[/] / [dim]{disk.total / (1024**3):.1f} GB[/]   "
                    f"Free: [green]{disk.free / (1024**3):.1f} GB[/]\n\n"
                    f"  [bold]📊 Status:[/]  {status_str}",
                    title="[bold]🖥️  Live System Dashboard[/]",
                    subtitle="[dim]Auto-refreshing every 2s[/]",
                    border_style="bright_green",
                    box=box.DOUBLE_EDGE,
                    padding=(1, 2)
                )
                return dashboard

            try:
                with Live(build_system_dashboard(), console=console, refresh_per_second=1, transient=False) as live:
                    for _ in range(15):  # 30 seconds of live updates
                        time.sleep(2)
                        live.update(build_system_dashboard())
            except KeyboardInterrupt:
                pass
            console.print("\n  [dim]Dashboard stopped.[/]")
            press_enter()

        elif choice == '4':
            return
        else:
            console.print("[red]  Invalid choice. Please enter 1-4.[/]")
            time.sleep(1)


# ─────────────────────────────────────────────────────────────
# FEATURE 6: RAG VISUALIZER (Interactive Terminal)
# ─────────────────────────────────────────────────────────────

def run_rag_visualizer():
    clear_screen()
    console.print(Panel(
        "[bold white]RAG VISUALIZER[/]\n[dim]Interactive Resource Allocation Graph Builder & Analyzer[/]",
        border_style="bright_blue", box=box.DOUBLE_EDGE, padding=(1, 4)
    ))

    nodes = []
    edges = []

    while True:
        console.print("\n[bold]  RAG Visualizer Menu:[/]\n")
        console.print(f"  [dim]Current: {len(nodes)} nodes, {len(edges)} edges[/]\n")
        console.print("  [cyan]1.[/] [bold]Add Process Node[/]")
        console.print("  [cyan]2.[/] [bold]Add Resource Node[/]")
        console.print("  [cyan]3.[/] [bold]Add Edge (Request / Assignment)[/]")
        console.print("  [cyan]4.[/] [bold]View Graph[/]")
        console.print("  [cyan]5.[/] [bold]Detect Deadlock[/]")
        console.print("  [cyan]6.[/] [bold]Load Preset[/]")
        console.print("  [cyan]7.[/] [bold]Clear Graph[/]")
        console.print("  [cyan]8.[/] [bold]Back to Main Menu[/]")

        choice = console.input("\n[cyan]  Your choice (1-8):[/] ").strip()

        if choice == '1':
            # Add Process
            pid = console.input("[cyan]  Process ID (e.g., P1):[/] ").strip().upper()
            if pid and not any(n['id'] == pid for n in nodes):
                nodes.append({'id': pid, 'type': 'process'})
                console.print(f"  [green]✓ Added process [bold]{pid}[/][/]")
            elif any(n['id'] == pid for n in nodes):
                console.print(f"  [red]Node {pid} already exists.[/]")
            else:
                console.print("  [red]Invalid ID.[/]")

        elif choice == '2':
            # Add Resource
            rid = console.input("[cyan]  Resource ID (e.g., R1):[/] ").strip().upper()
            if rid and not any(n['id'] == rid for n in nodes):
                nodes.append({'id': rid, 'type': 'resource'})
                console.print(f"  [green]✓ Added resource [bold]{rid}[/][/]")
            elif any(n['id'] == rid for n in nodes):
                console.print(f"  [red]Node {rid} already exists.[/]")
            else:
                console.print("  [red]Invalid ID.[/]")

        elif choice == '3':
            # Add Edge
            if not nodes:
                console.print("  [red]Add some nodes first.[/]")
                continue

            console.print("\n  [bold]Current Nodes:[/]")
            for n in nodes:
                icon = "[cyan]⬡[/]" if n['type'] == 'process' else "[green]■[/]"
                console.print(f"    {icon} {n['id']} ({n['type']})")

            console.print("\n  [dim]P→R = Request edge | R→P = Assignment edge[/]")
            src = console.input("[cyan]  Source:[/] ").strip().upper()
            tgt = console.input("[cyan]  Target:[/] ").strip().upper()

            if src and tgt:
                # Auto-add nodes if they don't exist
                if not any(n['id'] == src for n in nodes):
                    ntype = 'process' if src.startswith('P') else 'resource'
                    nodes.append({'id': src, 'type': ntype})
                    console.print(f"  [dim]Auto-created {ntype} node: {src}[/]")
                if not any(n['id'] == tgt for n in nodes):
                    ntype = 'process' if tgt.startswith('P') else 'resource'
                    nodes.append({'id': tgt, 'type': ntype})
                    console.print(f"  [dim]Auto-created {ntype} node: {tgt}[/]")

                edges.append({'source': src, 'target': tgt})

                src_type = next((n['type'] for n in nodes if n['id'] == src), 'process')
                label = 'requests' if src_type == 'process' else 'assigned to'
                console.print(f"  [green]✓ Added edge: {src} ──({label})──▶ {tgt}[/]")
            else:
                console.print("  [red]Invalid source or target.[/]")

        elif choice == '4':
            # View Graph
            if not nodes:
                console.print("  [red]Graph is empty. Add nodes and edges first.[/]")
                continue

            console.print()
            console.print(Panel(
                render_rag_ascii(nodes, edges, None),
                title="[bold]Resource Allocation Graph[/]",
                border_style="bright_blue", box=box.ROUNDED, padding=(1, 2)
            ))

            # Also show node and edge summary
            summary_table = Table(box=box.SIMPLE, show_header=False, border_style="dim")
            summary_table.add_column("Label", style="bold")
            summary_table.add_column("Value", style="cyan")
            proc_count = sum(1 for n in nodes if n['type'] == 'process')
            res_count = sum(1 for n in nodes if n['type'] == 'resource')
            summary_table.add_row("Processes", str(proc_count))
            summary_table.add_row("Resources", str(res_count))
            summary_table.add_row("Edges", str(len(edges)))
            console.print(summary_table)

        elif choice == '5':
            # Detect Deadlock
            if not nodes or not edges:
                console.print("  [red]Need nodes and edges to detect deadlock.[/]")
                continue

            console.print()
            console.print(Rule("[bold]Running DFS Cycle Detection[/]", style="blue"))
            time.sleep(0.5)

            deadlock, processes_involved, cycle_path = detect_deadlock(nodes, edges)

            # Show graph with cycle highlighted
            console.print()
            console.print(Panel(
                render_rag_ascii(nodes, edges, cycle_path if deadlock else None),
                title="[bold]RAG Analysis Result[/]",
                border_style="red" if deadlock else "green", box=box.ROUNDED, padding=(1, 2)
            ))

            console.print()
            if deadlock:
                cycle_str = " → ".join(cycle_path) + " → " + cycle_path[0] if cycle_path else "N/A"
                proc_str = ", ".join(processes_involved) if processes_involved else "N/A"
                console.print(Panel(
                    f"[bold bright_red]🔴 DEADLOCK DETECTED![/]\n\n"
                    f"[white]Cycle Path:[/]     [bold red]{cycle_str}[/]\n"
                    f"[white]Processes:[/]      [bold red]{proc_str}[/]",
                    border_style="red", box=box.DOUBLE_EDGE, padding=(1, 4)
                ))
            else:
                console.print(Panel(
                    "[bold bright_green]🟢 NO DEADLOCK FOUND[/]\n\n"
                    "[white]No cycles detected in the Resource Allocation Graph.\n"
                    "The system is free from deadlock.[/]",
                    border_style="green", box=box.DOUBLE_EDGE, padding=(1, 4)
                ))

        elif choice == '6':
            # Load Preset
            console.print("\n[bold]  Available Presets:[/]")
            console.print("  [cyan]1.[/] Deadlock Scenario (P1,P2,P3 + R1,R2)")
            console.print("  [cyan]2.[/] Safe Scenario (No Deadlock)")
            console.print("  [cyan]3.[/] Complex Deadlock (3-Process Cycle)")

            preset_choice = console.input("\n[cyan]  Choose preset (1-3):[/] ").strip()
            if preset_choice in PRESETS:
                preset = PRESETS[preset_choice]
                nodes = [n.copy() for n in preset['nodes']]
                edges = [e.copy() for e in preset['edges']]
                console.print(f"  [green]✓ Loaded preset: [bold]{preset['name']}[/][/]")
                console.print(f"    {len(nodes)} nodes, {len(edges)} edges")
            else:
                console.print("  [red]Invalid preset choice.[/]")

        elif choice == '7':
            # Clear Graph
            nodes = []
            edges = []
            console.print("  [green]✓ Graph cleared.[/]")

        elif choice == '8':
            return
        else:
            console.print("[red]  Invalid choice. Please enter 1-8.[/]")
            time.sleep(1)


# ─────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────

def show_banner():
    banner_lines = [
        "    ╔═══════════════════════════════════════════════════════════════════════════════╗",
        "    ║                                                                               ║",
        "    ║   ██████╗ ███████╗ █████╗ ██████╗ ██╗      ██████╗  ██████╗██╗  ██╗           ║",
        "    ║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝           ║",
        "    ║   ██║  ██║█████╗  ███████║██║  ██║██║     ██║   ██║██║     █████╔╝            ║",
        "    ║   ██║  ██║██╔══╝  ██╔══██║██║  ██║██║     ██║   ██║██║     ██╔═██╗            ║",
        "    ║   ██████╔╝███████╗██║  ██║██████╔╝███████╗╚██████╔╝╚██████╗██║  ██╗           ║",
        "    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝           ║",
        "    ║                                                                               ║",
        "    ║   ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗                     ║",
        "    ║   ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝                     ║",
        "    ║      ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║                        ║",
        "    ║      ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║                        ║",
        "    ║      ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║                        ║",
        "    ║      ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝                        ║",
        "    ║                                                                               ║",
        "    ║            DEADLOCK PREVENTION & DETECTION TOOLKIT                             ║",
        "    ║                                                                               ║",
        "    ╚═══════════════════════════════════════════════════════════════════════════════╝",
    ]
    # Cascade reveal with color cycling
    colors = itertools.cycle(["bright_cyan", "bright_blue", "bright_magenta", "bright_cyan"])
    console.print()
    for line in banner_lines:
        color = next(colors)
        if "DEADLOCK PREVENTION" in line:
            # Highlight the title line specially
            console.print(f"[bold bright_white]{line}[/]")
        elif "Operating Systems" in line:
            console.print(f"[dim]{line}[/]")
        else:
            console.print(f"[bold {color}]{line}[/]")
        time.sleep(0.03)
    console.print()


def main_menu():
    first_load = True
    while True:
        if first_load:
            clear_screen()
            # First load: show a brief loading animation
            progress_animation("Loading Deadlock Toolkit", steps=15, duration=0.8)
            clear_screen()
            first_load = False
        else:
            transition_screen()

        show_banner()

        console.print()
        menu_items = Table(box=box.ROUNDED, border_style="bright_cyan", show_header=False, padding=(0, 3))
        menu_items.add_column("Option", style="bold cyan", justify="center", width=6)
        menu_items.add_column("Feature", style="bold white", width=28)
        menu_items.add_column("Description", style="dim", width=50)

        menu_items.add_row("1", "🏦 Banker's Algorithm", "Safety check — prevent deadlocks before they occur")
        menu_items.add_row("2", "🔍 Deadlock Detection", "Detect cycles in Resource Allocation Graphs")
        menu_items.add_row("3", "🔧 Deadlock Recovery", "Break deadlock with termination or preemption")
        menu_items.add_row("4", "⚡ Simulation Engine", "Live step-by-step scenario simulation")
        menu_items.add_row("5", "🖥️  Live Process Monitor", "Scan real system processes & detect deadlocks")
        menu_items.add_row("6", "📊 RAG Visualizer", "Interactive Resource Allocation Graph builder")
        menu_items.add_row("7", "🚪 Exit", "Exit the toolkit")

        console.print(Align.center(menu_items))

        console.print()
        choice = console.input("[bold cyan]  Enter your choice (1-7): [/]").strip()

        if choice == '1':
            with_repeat(run_bankers, "Banker's Algorithm")
        elif choice == '2':
            with_repeat(run_detection, "Deadlock Detection")
        elif choice == '3':
            with_repeat(run_recovery, "Deadlock Recovery")
        elif choice == '4':
            with_repeat(run_simulation, "Simulation Engine")
        elif choice == '5':
            run_live_monitor()
        elif choice == '6':
            run_rag_visualizer()
        elif choice == '7':
            transition_screen()
            # Animated goodbye
            goodbye_lines = [
                "",
                "  ╔══════════════════════════════════════════════════════╗",
                "  ║                                                      ║",
                "  ║   ⚡ Terminating Deadlock System.                   ║",
                "  ║                                                      ║",
                "  ║   Thank you for using the Deadlock Toolkit!          ║",
                "  ║   All processes released. System is now SAFE.        ║",
                "  ║                                                      ║",
                "  ╚══════════════════════════════════════════════════════╝",
                "",
            ]
            colors = itertools.cycle(["bright_cyan", "bright_blue", "bright_magenta"])
            for line in goodbye_lines:
                console.print(f"[bold {next(colors)}]{line}[/]")
                time.sleep(0.08)
            console.print()
            sys.exit(0)
        else:
            console.print("[red]  Invalid choice. Please enter 1-7.[/]")
            time.sleep(1)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[dim]Exited.[/]")
        sys.exit(0)
