"""
Visualization engine for drawing Resource Allocation Graphs and animations.
"""
import tkinter as tk
import math


class VisualizationPanel(tk.Canvas):
    """
    Canvas-based visualization panel for drawing nodes, edges, and animating packets.
    """
    
    def __init__(self, parent, width=600, height=500, **kwargs):
        """Initialize the visualization canvas."""
        # Remove 'bg' from kwargs if it exists to avoid conflict
        kwargs.pop('bg', None)
        
        super().__init__(
            parent,
            width=width,
            height=height,
            bg='#0d1119',
            highlightthickness=0,
            **kwargs
        )
        self.width = width
        self.height = height
        self.node_positions = {}  # {'node_id': (x, y)}
        self.node_objects = {}    # {'node_id': canvas_object_id}
        self.edge_objects = {}    # {('src', 'tgt'): canvas_object_id}
        self.animations = []      # List of active animations
    
    def draw_grid_background(self):
        """Draw a subtle grid background."""
        grid_spacing = 40
        for x in range(0, self.width, grid_spacing):
            self.create_line(x, 0, x, self.height, fill="#1a2839", width=1)
        for y in range(0, self.height, grid_spacing):
            self.create_line(0, y, self.width, y, fill="#1a2839", width=1)
    
        
        # Draw grid background
        self.draw_grid_background()
        
    def clear_canvas(self):
        """Remove all drawn elements."""
        self.delete("all")
        self.node_positions.clear()
        self.node_objects.clear()
        self.edge_objects.clear()
        self.animations.clear()
    
    def layout_graph(self, nodes, edges):
        """
        Calculate node positions using circular layout for processes and resources.
        
        Args:
            nodes: List of node dicts {'id': str, 'type': 'process'|'resource'}
            edges: List of edge dicts (not used for layout, but validates graph)
        """
        if not nodes:
            return
        
        # Separate processes and resources
        processes = [n for n in nodes if n['type'] == 'process']
        resources = [n for n in nodes if n['type'] == 'resource']
        
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Place processes in a circle on the left
        if processes:
            radius = min(self.width, self.height) / 3
            angle_step = 2 * math.pi / len(processes)
            for i, proc in enumerate(processes):
                angle = i * angle_step - math.pi / 2
                x = center_x - radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.node_positions[proc['id']] = (x, y)
        
        # Place resources in a circle on the right
        if resources:
            radius = min(self.width, self.height) / 3
            angle_step = 2 * math.pi / len(resources)
            for i, res in enumerate(resources):
                angle = i * angle_step - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.node_positions[res['id']] = (x, y)
    
    def draw_process(self, pid, x, y, highlight=False):
        """
        Draw a process node (circle).
        
        Args:
            pid: Process ID
            x: X coordinate
            y: Y coordinate
            highlight: If True, fill with red; else cyan
        """
        radius = 25
        fill_color = '#ff4444' if highlight else '#00ff88'
        outline_color = '#ff0000' if highlight else '#00ffff'
        
        circle = self.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=fill_color,
            outline=outline_color,
            width=3
        )
        # Draw label
        label = self.create_text(x, y, text=pid, fill='white', font=('Arial', 11, 'bold'))
        
        self.node_positions[pid] = (x, y)
        self.node_objects[pid] = (circle, label)
        return circle, label
    
    def draw_resource(self, rid, x, y, highlight=False):
        """
        Draw a resource node (square).
        
        Args:
            rid: Resource ID
            x: X coordinate
            y: Y coordinate
            highlight: If True, fill with red; else green
        """
        size = 25
        fill_color = '#ff4444' if highlight else '#00ff88'
        outline_color = '#ff0000' if highlight else '#00ffff'
        
        square = self.create_rectangle(
            x - size, y - size,
            x + size, y + size,
            fill=fill_color,
            outline=outline_color,
            width=3
        )
        # Draw label
        label = self.create_text(x, y, text=rid, fill='white', font=('Arial', 11, 'bold'))
        
        self.node_positions[rid] = (x, y)
        self.node_objects[rid] = (square, label)
        return square, label
    
    def draw_edge(self, src, tgt, in_cycle=False):
        """
        Draw a directed edge from src to tgt.
        
        Args:
            src: Source node ID
            tgt: Target node ID
            in_cycle: If True, draw in red; else cyan
        """
        if src not in self.node_positions or tgt not in self.node_positions:
            return None
        
        x1, y1 = self.node_positions[src]
        x2, y2 = self.node_positions[tgt]
        
        # Calculate arrow endpoints (shorten to not overlap nodes)
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 1:
            dist = 1
        
        # Shorten line to end before target node
        offset = 30
        x1_adj = x1 + (dx / dist) * offset
        y1_adj = y1 + (dy / dist) * offset
        x2_adj = x2 - (dx / dist) * offset
        y2_adj = y2 - (dy / dist) * offset
        
        color = '#ff4444' if in_cycle else '#00d9ff'
        width = 3 if in_cycle else 2
        
        # Draw line
        line = self.create_line(
            x1_adj, y1_adj, x2_adj, y2_adj,
            fill=color, width=width, arrow=tk.LAST, arrowshape=(18, 22, 12)
        )
        
        self.edge_objects[(src, tgt)] = line
        return line
    
    def animate_packet(self, src, tgt, duration=1.0, callback=None):
        """
        Animate a small packet moving from src to tgt.
        
        Args:
            src: Source node ID
            tgt: Target node ID
            duration: Animation duration in seconds
            callback: Optional callback when animation completes
        """
        if src not in self.node_positions or tgt not in self.node_positions:
            return
        
        x1, y1 = self.node_positions[src]
        x2, y2 = self.node_positions[tgt]
        
        # Shorten animation path to avoid node overlap
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 1:
            dist = 1
        
        offset = 30
        x1 = x1 + (dx / dist) * offset
        y1 = y1 + (dy / dist) * offset
        x2 = x2 - (dx / dist) * offset
        y2 = y2 - (dy / dist) * offset
        
        # Create packet (small circle)
        packet = self.create_oval(
            x1 - 6, y1 - 6,
            x1 + 6, y1 + 6,
            fill='#ffff00',
            outline='#ffaa00',
            width=2
        )
        
        # Animation parameters
        start_time = self.after(0, lambda: None)  # Get reference time
        import time
        start_ms = int(time.time() * 1000)
        
        def animate_step():
            """Animation step function."""
            import time
            now_ms = int(time.time() * 1000)
            elapsed = (now_ms - start_ms) / 1000.0
            progress = min(elapsed / duration, 1.0)
            
            # Linear interpolation
            x = x1 + (x2 - x1) * progress
            y = y1 + (y2 - y1) * progress
            
            # Move packet
            self.coords(packet, x - 6, y - 6, x + 6, y + 6)
            
            if progress < 1.0:
                # Continue animation
                self.after(16, animate_step)  # ~60 FPS
            else:
                # Animation complete, delete packet
                self.delete(packet)
                if callback:
                    callback()
        
        animate_step()
    
    def highlight_deadlock(self, cycle_nodes):
        """
        Highlight nodes involved in a deadlock cycle with red color.
        
        Args:
            cycle_nodes: List of node IDs in the cycle
        """
        for node_id in cycle_nodes:
            if node_id in self.node_objects:
                shape, label = self.node_objects[node_id]
                self.itemconfig(shape, fill='#ff4444', outline='#ff0000')
    
    def draw_from_scratch(self, nodes, edges, cycle_nodes=None):
        """
        Clear and redraw entire graph.
        
        Args:
            nodes: List of node dicts
            edges: List of edge dicts
            cycle_nodes: Optional list of nodes in cycle to highlight
        """
        if cycle_nodes is None:
            cycle_nodes = []
        
        self.clear_canvas()
        self.layout_graph(nodes, edges)
        
        # Draw all nodes
        for node in nodes:
            nid = node['id']
            if nid not in self.node_positions:
                continue
            
            x, y = self.node_positions[nid]
            highlight = nid in cycle_nodes
            
            if node['type'] == 'process':
                self.draw_process(nid, x, y, highlight=highlight)
            else:  # resource
                self.draw_resource(nid, x, y, highlight=highlight)
        
        # Draw all edges
        for edge in edges:
            src = edge['source']
            tgt = edge['target']
            in_cycle = (src in cycle_nodes and tgt in cycle_nodes)
            self.draw_edge(src, tgt, in_cycle=in_cycle)
