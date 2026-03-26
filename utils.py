"""
Utility functions for data generation and presets.
"""
import random


def generate_random_bankers_data(n=None, m=None):
    """
    Generate a valid random Banker's Algorithm scenario.
    
    Args:
        n: Number of processes (if None, random 3-6)
        m: Number of resource types (if None, random 2-4)
    
    Returns:
        (processes, resources, allocation, max_matrix, available)
    """
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
    """
    Generate a random Resource Allocation Graph, optionally forcing deadlock.
    
    Args:
        deadlock: None (random), True (force deadlock), or False (force safe)
    
    Returns:
        (nodes, edges)
        - nodes: List of {'id': str, 'type': 'process'|'resource'}
        - edges: List of {'source': str, 'target': str}
    """
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
            edges.append({'source': p, 'target': r})
            edges.append({'source': r, 'target': next_p})
        
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
    """
    Generate a random deadlocked scenario for recovery.
    
    Returns:
        (deadlocked_processes, resource_labels, allocation, available, num_resources)
    """
    num_procs = random.randint(2, 4)
    num_resources = random.randint(2, 3)
    deadlocked = [f'P{i}' for i in range(num_procs)]
    resource_labels = [chr(65 + i) for i in range(num_resources)]
    allocation = [[random.randint(1, 4) for _ in range(num_resources)] for _ in range(num_procs)]
    available = [random.randint(0, 2) for _ in range(num_resources)]
    return deadlocked, resource_labels, allocation, available, num_resources


# Preset RAG scenarios
RAG_PRESETS = {
    '1': {
        'name': 'Deadlock Scenario',
        'nodes': [
            {'id': 'P1', 'type': 'process'},
            {'id': 'P2', 'type': 'process'},
            {'id': 'P3', 'type': 'process'},
            {'id': 'R1', 'type': 'resource'},
            {'id': 'R2', 'type': 'resource'},
        ],
        'edges': [
            {'source': 'P1', 'target': 'R1'},
            {'source': 'R1', 'target': 'P2'},
            {'source': 'P2', 'target': 'R2'},
            {'source': 'R2', 'target': 'P1'},
            {'source': 'P3', 'target': 'R2'},
        ],
    },
    '2': {
        'name': 'Safe Scenario (No Deadlock)',
        'nodes': [
            {'id': 'P1', 'type': 'process'},
            {'id': 'P2', 'type': 'process'},
            {'id': 'R1', 'type': 'resource'},
            {'id': 'R2', 'type': 'resource'},
        ],
        'edges': [
            {'source': 'P1', 'target': 'R1'},
            {'source': 'R2', 'target': 'P2'},
        ],
    },
    '3': {
        'name': 'Complex Deadlock (3 Process Cycle)',
        'nodes': [
            {'id': 'P1', 'type': 'process'},
            {'id': 'P2', 'type': 'process'},
            {'id': 'P3', 'type': 'process'},
            {'id': 'R1', 'type': 'resource'},
            {'id': 'R2', 'type': 'resource'},
            {'id': 'R3', 'type': 'resource'},
        ],
        'edges': [
            {'source': 'P1', 'target': 'R1'},
            {'source': 'R1', 'target': 'P2'},
            {'source': 'P2', 'target': 'R2'},
            {'source': 'R2', 'target': 'P3'},
            {'source': 'P3', 'target': 'R3'},
            {'source': 'R3', 'target': 'P1'},
        ],
    },
}
