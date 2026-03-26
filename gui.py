"""
Main GUI application for the Deadlock Toolkit.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import customtkinter as ctk
from datetime import datetime
from algorithms import bankers_safety_check, detect_deadlock, recover_deadlock
from utils import (
    generate_random_bankers_data,
    generate_random_rag,
    generate_random_recovery_data,
    RAG_PRESETS
)
from visualization import VisualizationPanel


class DeadlockApp(ctk.CTk):
    """Main application window for Deadlock Toolkit."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Configure window
        self.title("Deadlock Prevention & Detection Toolkit")
        self.geometry("1600x900")
        ctk.set_appearance_mode("dark")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # State variables
        self.current_data = {}  # Store current algorithm data
        self.simulation_running = False
        
        # Center window on screen
        self.after(100, self.center_window)
    
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_sidebar(self):
        """Create the left sidebar with navigation buttons."""
        sidebar = ctk.CTkFrame(self, fg_color="#0f1419", width=220)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Main container with padding
        container = ctk.CTkFrame(sidebar, fg_color="#0f1419")
        container.pack(fill="both", expand=True, padx=15, pady=20)
        container.grid_rowconfigure(5, weight=1)
        
        # Logo/Title section
        title_frame = ctk.CTkFrame(container, fg_color="#0f1419")
        title_frame.pack(fill="x", pady=(0, 20))
        
        logo = ctk.CTkLabel(
            title_frame,
            text="🔗",
            font=("Arial", 40, "bold"),
            text_color="#00d9ff"
        )
        logo.pack(pady=(0, 10))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Deadlock\nToolkit",
            font=("Arial", 22, "bold"),
            text_color="#ffffff",
            text_color_disabled="#00d9ff"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="OS Simulation",
            font=("Arial", 11),
            text_color="#888888"
        )
        subtitle.pack()
        
        # Separator
        sep1 = ctk.CTkFrame(container, height=1, fg_color="#2a3f5f")
        sep1.pack(fill="x", pady=15)
        
        # Buttons section with label
        buttons_label = ctk.CTkLabel(
            container,
            text="ALGORITHMS",
            font=("Arial", 10, "bold"),
            text_color="#888888"
        )
        buttons_label.pack(fill="x", pady=(10, 15))
        
        # Algorithm buttons
        buttons = [
            ("🏦 Banker's Algorithm", self.on_bankers_clicked, "#1f3a5c"),
            ("🔍 Deadlock Detection", self.on_detection_clicked, "#1f3a5c"),
            ("🔧 Recovery", self.on_recovery_clicked, "#1f3a5c"),
            ("⚡ Simulation", self.on_simulation_clicked, "#1f3a5c"),
        ]
        
        for btn_text, btn_cmd, btn_color in buttons:
            btn = ctk.CTkButton(
                container,
                text=btn_text,
                command=btn_cmd,
                font=("Arial", 12, "bold"),
                height=50,
                corner_radius=10,
                fg_color=btn_color,
                hover_color="#2a5a8c",
                text_color="#ffffff",
                border_width=1,
                border_color="#00d9ff"
            )
            btn.pack(pady=8, fill="x")
        
        # Spacer
        spacer = ctk.CTkFrame(container, fg_color="#0f1419", height=20)
        spacer.pack(fill="both", expand=True)
        
        # Bottom section
        sep2 = ctk.CTkFrame(container, height=1, fg_color="#2a3f5f")
        sep2.pack(fill="x", pady=15)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            container,
            text="📋 Clear Logs",
            command=self.clear_logs,
            font=("Arial", 11, "bold"),
            height=45,
            corner_radius=10,
            fg_color="#3f2a2a",
            hover_color="#5f3a3a",
            text_color="#ffaaaa",
            border_width=1,
            border_color="#ff6666"
        )
        clear_btn.pack(pady=10, fill="x")
    
    def create_main_content(self):
        """Create the main content area with visualization and logs."""
        # Main background
        main_frame = ctk.CTkFrame(self, fg_color="#0a0e1a")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main_frame.grid_rowconfigure(0, weight=3)
        main_frame.grid_rowconfigure(1, weight=2)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Top section - Visualization
        viz_section = ctk.CTkFrame(main_frame, fg_color="#0a0e1a")
        viz_section.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        viz_section.grid_rowconfigure(1, weight=1)
        viz_section.grid_columnconfigure(0, weight=1)
        
        # Visualization header
        viz_header_frame = ctk.CTkFrame(viz_section, fg_color="#0a0e1a")
        viz_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        viz_label = ctk.CTkLabel(
            viz_header_frame,
            text="📊 Visualization Panel",
            font=("Arial", 14, "bold"),
            text_color="#00d9ff"
        )
        viz_label.pack(side="left")
        
        # Visualization canvas with border
        viz_border = ctk.CTkFrame(viz_section, fg_color="#1a2332", border_width=2, border_color="#00d9ff")
        viz_border.grid(row=1, column=0, sticky="nsew")
        viz_border.grid_rowconfigure(0, weight=1)
        viz_border.grid_columnconfigure(0, weight=1)
        
        self.viz_panel = VisualizationPanel(viz_border, width=1100, height=350)
        self.viz_panel.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Bottom section - Log
        log_section = ctk.CTkFrame(main_frame, fg_color="#0a0e1a")
        log_section.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        log_section.grid_rowconfigure(1, weight=1)
        log_section.grid_columnconfigure(0, weight=1)
        
        # Log header
        log_header_frame = ctk.CTkFrame(log_section, fg_color="#0a0e1a")
        log_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        log_label = ctk.CTkLabel(
            log_header_frame,
            text="📝 Execution Log",
            font=("Arial", 14, "bold"),
            text_color="#00d9ff"
        )
        log_label.pack(side="left")
        
        # Log container with border
        log_border = ctk.CTkFrame(log_section, fg_color="#1a2332", border_width=2, border_color="#00d9ff")
        log_border.grid(row=1, column=0, sticky="nsew")
        log_border.grid_rowconfigure(0, weight=1)
        log_border.grid_columnconfigure(0, weight=1)
        
        # Scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(
            log_border,
            height=15,
            bg="#0d1119",
            fg="#ffffff",
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground="#00d9ff",
            selectbackground="#00d9ff",
            selectforeground="#0d1119"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Configure text tags for colors
        self.log_text.tag_config("success", foreground="#00ff55", font=("Consolas", 10))
        self.log_text.tag_config("error", foreground="#ff4444", font=("Consolas", 10))
        self.log_text.tag_config("info", foreground="#00d9ff", font=("Consolas", 10))
        self.log_text.tag_config("warning", foreground="#ffdd55", font=("Consolas", 10))
    
    def append_log(self, message, level="info"):
        """
        Append a message to the log panel with timestamp and color.
        
        Args:
            message: Text to append
            level: 'success', 'error', 'warning', or 'info'
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Emoji indicators
        emoji_map = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️ ",
            "info": "ℹ️ "
        }
        emoji = emoji_map.get(level, "•")
        
        log_line = f"[{timestamp}] {emoji} {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_line, level)
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state=tk.NORMAL)
    
    def clear_logs(self):
        """Clear the log panel."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.NORMAL)
    
    # =========================================================================
    # BANKER'S ALGORITHM HANDLER
    # =========================================================================
    
    def on_bankers_clicked(self):
        """Handle Banker's Algorithm button click."""
        self.clear_logs()
        self.viz_panel.clear_canvas()
        self.append_log("🏦 Banker's Algorithm - Safety Check", "info")
        self.append_log("Generating random scenario...", "info")
        
        # Generate random data
        processes, resources, allocation, max_matrix, available = generate_random_bankers_data()
        
        # Display generated scenario
        self.append_log(f"Generated: {len(processes)} processes, {len(resources)} resources", "info")
        self.append_log("", "info")
        
        # Show Allocation Matrix
        self.append_log("=== ALLOCATION MATRIX ===", "warning")
        self._display_matrix(allocation, processes, resources)
        self.append_log("", "info")
        
        # Show Max Matrix
        self.append_log("=== MAX MATRIX ===", "warning")
        self._display_matrix(max_matrix, processes, resources)
        self.append_log("", "info")
        
        # Show Available
        self.append_log(f"Available: {dict(zip(resources, available))}", "warning")
        self.append_log("", "info")
        
        # Run algorithm
        self.append_log("Running Banker's Algorithm Safety Check...", "info")
        safe, safe_sequence, need_matrix, algo_log = bankers_safety_check(
            processes, resources, allocation, max_matrix, available
        )
        
        # Display algorithm log
        for line in algo_log:
            if "SAFE" in line:
                self.append_log(line, "success")
            elif "UNSAFE" in line:
                self.append_log(line, "error")
            else:
                self.append_log(line, "info")
        
        self.append_log("", "info")
        
        # Show result
        if safe:
            seq_str = " → ".join(safe_sequence)
            self.append_log("✅ SYSTEM IS SAFE", "success")
            self.append_log(f"Safe Sequence: {seq_str}", "success")
        else:
            self.append_log("❌ SYSTEM IS UNSAFE", "error")
            self.append_log("No safe sequence exists. The system may deadlock.", "error")
        
        self.current_data = {
            'type': 'bankers',
            'processes': processes,
            'resources': resources,
            'allocation': allocation,
            'max_matrix': max_matrix,
            'available': available,
            'safe': safe,
            'sequence': safe_sequence
        }
    
    # =========================================================================
    # DEADLOCK DETECTION HANDLER
    # =========================================================================
    
    def on_detection_clicked(self):
        """Handle Deadlock Detection button click."""
        self.clear_logs()
        self.viz_panel.clear_canvas()
        self.append_log("🔍 Deadlock Detection - RAG Analysis", "info")
        
        # Randomly choose to use preset or generate
        import random
        use_preset = random.choice([True, False])
        
        if use_preset:
            self.append_log("Loading preset scenario...", "info")
            preset_key = random.choice(['1', '2', '3'])
            preset = RAG_PRESETS[preset_key]
            nodes = preset['nodes']
            edges = preset['edges']
            self.append_log(f"Loaded: {preset['name']}", "info")
        else:
            self.append_log("Generating random RAG...", "info")
            nodes, edges = generate_random_rag()
            num_procs = sum(1 for n in nodes if n['type'] == 'process')
            num_res = sum(1 for n in nodes if n['type'] == 'resource')
            self.append_log(f"Generated: {num_procs} processes, {num_res} resources, {len(edges)} edges", "info")
        
        self.append_log("", "info")
        
        # Display graph structure
        self.append_log("=== GRAPH STRUCTURE ===", "warning")
        processes = [n['id'] for n in nodes if n['type'] == 'process']
        resources = [n['id'] for n in nodes if n['type'] == 'resource']
        self.append_log(f"Processes: {', '.join(processes)}", "info")
        self.append_log(f"Resources: {', '.join(resources)}", "info")
        self.append_log("Edges:", "info")
        for edge in edges:
            self.append_log(f"  {edge['source']} → {edge['target']}", "info")
        self.append_log("", "info")
        
        # Run detection
        self.append_log("Running deadlock detection (DFS cycle detection)...", "info")
        deadlock, processes_involved, cycle_path = detect_deadlock(nodes, edges)
        self.append_log("", "info")
        
        # Draw graph
        self.viz_panel.draw_from_scratch(nodes, edges, cycle_path if deadlock else [])
        
        # Show result
        if deadlock:
            cycle_str = " → ".join(cycle_path) + (" → " + cycle_path[0] if cycle_path else "")
            proc_str = ", ".join(processes_involved) if processes_involved else "N/A"
            
            self.append_log("🔴 DEADLOCK DETECTED!", "error")
            self.append_log(f"Cycle Path: {cycle_str}", "error")
            self.append_log(f"Processes: {proc_str}", "error")
            
            # Animate packets along cycle
            if len(cycle_path) >= 2:
                for i in range(len(cycle_path)):
                    src = cycle_path[i]
                    tgt = cycle_path[(i + 1) % len(cycle_path)]
                    self.after(500 * i, lambda s=src, t=tgt: self.viz_panel.animate_packet(s, t, duration=0.8))
        else:
            self.append_log("🟢 NO DEADLOCK FOUND", "success")
            self.append_log("No cycles detected in the Resource Allocation Graph.", "success")
        
        self.current_data = {
            'type': 'detection',
            'nodes': nodes,
            'edges': edges,
            'deadlock': deadlock,
            'cycle_path': cycle_path,
            'processes_involved': processes_involved
        }
    
    # =========================================================================
    # RECOVERY HANDLER
    # =========================================================================
    
    def on_recovery_clicked(self):
        """Handle Deadlock Recovery button click."""
        self.clear_logs()
        self.viz_panel.clear_canvas()
        self.append_log("🔧 Deadlock Recovery", "info")
        
        # Strategy selection (cycle through for demo)
        strategies = [
            ('terminate-all', 'Terminate All'),
            ('terminate-one-by-one', 'One-by-One Termination'),
            ('preemption', 'Resource Preemption')
        ]
        
        import random
        strategy_key, strategy_name = random.choice(strategies)
        
        self.append_log(f"Selected Strategy: {strategy_name}", "warning")
        self.append_log("", "info")
        
        # Generate deadlock scenario
        self.append_log("Generating deadlocked scenario...", "info")
        deadlocked, resource_labels, allocation, available, num_resources = generate_random_recovery_data()
        
        self.append_log(f"Deadlocked Processes: {', '.join(deadlocked)}", "info")
        self.append_log(f"Resources: {', '.join(resource_labels)}", "info")
        self.append_log("", "info")
        
        # Display allocation
        self.append_log("=== ALLOCATION MATRIX (Deadlocked Processes) ===", "warning")
        self._display_matrix(allocation, deadlocked, resource_labels)
        self.append_log("", "info")
        
        # Display available
        self.append_log(f"Available: {dict(zip(resource_labels, available))}", "warning")
        self.append_log("", "info")
        
        # Prepare full allocation (indexed by process number)
        max_idx = max(int(p.replace('P', '')) for p in deadlocked) + 1
        full_allocation = [[0] * num_resources for _ in range(max_idx)]
        for i, pid in enumerate(deadlocked):
            idx = int(pid.replace('P', ''))
            full_allocation[idx] = allocation[i]
        
        # Run recovery
        self.append_log(f"Executing {strategy_name}...", "info")
        _, steps, updated_alloc = recover_deadlock(
            full_allocation, available, deadlocked, strategy_key
        )
        self.append_log("", "info")
        
        # Display recovery steps
        self.append_log("=== RECOVERY STEPS ===", "warning")
        for i, step in enumerate(steps, 1):
            level = "success" if "Deadlock resolved" in step or "recovered" in step else "warning"
            if "terminated" in step.lower() or "preempted" in step.lower():
                level = "error"
            self.append_log(f"Step {i}: {step}", level)
        self.append_log("", "info")
        
        self.append_log("✅ RECOVERY COMPLETE", "success")
        self.append_log(f"Strategy Used: {strategy_name}", "success")
        
        self.current_data = {
            'type': 'recovery',
            'deadlocked': deadlocked,
            'strategy': strategy_key,
            'steps': steps
        }
    
    # =========================================================================
    # SIMULATION HANDLER
    # =========================================================================
    
    def on_simulation_clicked(self):
        """Handle Simulation button click."""
        self.clear_logs()
        self.viz_panel.clear_canvas()
        self.append_log("⚡ Deadlock Simulation Engine", "info")
        
        # Generate system
        self.append_log("Generating system state...", "info")
        import random
        num_processes = random.randint(2, 4)
        num_resources = random.randint(2, 3)
        
        processes = [f"P{i}" for i in range(num_processes)]
        resources = [chr(65 + i) for i in range(num_resources)]
        
        total_resources = [random.randint(4, 11) for _ in range(num_resources)]
        allocation = [[0] * num_resources for _ in range(num_processes)]
        max_matrix = [
            [random.randint(0, total_resources[j]) for j in range(num_resources)]
            for _ in range(num_processes)
        ]
        available = total_resources[:]
        
        self.append_log(f"System: {num_processes} processes, {num_resources} resources", "info")
        self.append_log(f"Processes: {', '.join(processes)}", "info")
        self.append_log(f"Resources: {', '.join(resources)}", "info")
        self.append_log(f"Total Resources: {dict(zip(resources, total_resources))}", "warning")
        self.append_log("", "info")
        
        # Show initial state
        self.append_log("=== INITIAL STATE ===", "warning")
        self.append_log(f"Available: {dict(zip(resources, available))}", "info")
        self.append_log("", "info")
        
        # Simulation loop
        self.append_log("Running simulation (20 steps)...", "info")
        self.append_log("", "info")
        
        sim_logs = []
        for step in range(20):
            p_idx = random.randint(0, num_processes - 1)
            r_idx = random.randint(0, num_resources - 1)
            pid = processes[p_idx]
            rid = resources[r_idx]
            
            need = max_matrix[p_idx][r_idx] - allocation[p_idx][r_idx]
            
            if need > 0 and available[r_idx] > 0:
                amount = min(need, available[r_idx], random.randint(1, 2))
                allocation[p_idx][r_idx] += amount
                available[r_idx] -= amount
                
                safe, seq, _, _ = bankers_safety_check(
                    processes, resources, allocation, max_matrix, available
                )
                
                if safe:
                    seq_str = " → ".join(seq)
                    msg = f"Step {step+1}: ✅ Granted {amount}× {rid} to {pid}. Safe Sequence: {seq_str}"
                    self.append_log(msg, "success")
                    sim_logs.append(('safe', msg))
                else:
                    allocation[p_idx][r_idx] -= amount
                    available[r_idx] += amount
                    msg = f"Step {step+1}: ❌ Denied {amount}× {rid} to {pid}. Would be UNSAFE."
                    self.append_log(msg, "error")
                    sim_logs.append(('denied', msg))
            else:
                msg = f"Step {step+1}: ⏭ {pid} has no need for {rid}."
                self.append_log(msg, "warning")
                sim_logs.append(('skip', msg))
            
            # Small delay for readability
            self.update()
        
        self.append_log("", "info")
        
        # Final state
        final_safe, final_seq, _, _ = bankers_safety_check(
            processes, resources, allocation, max_matrix, available
        )
        
        self.append_log("=== FINAL STATE ===", "warning")
        self.append_log(f"Available: {dict(zip(resources, available))}", "info")
        
        if final_safe:
            self.append_log("✅ System remains SAFE", "success")
            seq_str = " → ".join(final_seq)
            self.append_log(f"Safe Sequence: {seq_str}", "success")
        else:
            self.append_log("⚠️ System is now UNSAFE", "error")
        
        self.current_data = {
            'type': 'simulation',
            'processes': processes,
            'resources': resources,
            'final_safe': final_safe,
            'logs': sim_logs
        }
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _display_matrix(self, matrix, row_labels, col_labels):
        """
        Display a matrix in the log.
        
        Args:
            matrix: 2D list
            row_labels: Labels for rows
            col_labels: Labels for columns
        """
        # Header row
        header = "   " + "  ".join(f"{label:>3}" for label in col_labels)
        self.append_log(header, "info")
        
        # Data rows
        for i, row_label in enumerate(row_labels):
            row_str = f"{row_label}: " + " ".join(f"{matrix[i][j]:>3}" for j in range(len(col_labels)))
            self.append_log(row_str, "info")


def run_app():
    """Create and run the application."""
    app = DeadlockApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
