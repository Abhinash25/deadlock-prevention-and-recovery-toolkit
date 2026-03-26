"""
Core deadlock detection and prevention algorithms.
These functions are UI-independent and can be used standalone.
"""


def bankers_safety_check(processes, resources, allocation, max_matrix, available):
    """
    Banker's Algorithm — Safety Check.
    
    Args:
        processes: List of process IDs (e.g., ['P0', 'P1', 'P2'])
        resources: List of resource types (e.g., ['A', 'B', 'C'])
        allocation: 2D list of currently allocated resources [process][resource]
        max_matrix: 2D list of maximum needed resources [process][resource]
        available: List of available resources [resource]
    
    Returns:
        (safe, safe_sequence, need_matrix, log)
        - safe: Boolean, True if system is in safe state
        - safe_sequence: List of processes in safe order (empty if unsafe)
        - need_matrix: 2D list of additional resources needed [process][resource]
        - log: List of log messages describing execution
    """
    n = len(processes)
    m = len(resources)

    # Calculate Need matrix
    need = [[max_matrix[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    
    work = available[:]
    finish = [False] * n
    safe_sequence = []
    log = []

    log.append(f"Initial Work (Available): {work}")

    count = 0
    while count < n:
        found = False
        for i in range(n):
            if not finish[i]:
                # Check if process i's needs can be satisfied
                if all(need[i][j] <= work[j] for j in range(m)):
                    log.append(f"Process {processes[i]} can be allocated. Need: {need[i]} <= Work: {work}")
                    # Process i can finish; release its resources
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
    """
    Detect deadlock using DFS-based cycle detection in Resource Allocation Graph.
    
    Args:
        nodes: List of node dicts with 'id' and 'type' (e.g., {'id': 'P1', 'type': 'process'})
        edges: List of edge dicts with 'source' and 'target' (e.g., {'source': 'P1', 'target': 'R1'})
    
    Returns:
        (deadlock, processes_involved, cycle_path)
        - deadlock: Boolean, True if cycle found
        - processes_involved: List of process IDs in the cycle
        - cycle_path: List of node IDs forming the cycle
    """
    # Build adjacency list
    adj = {n['id']: [] for n in nodes}
    for e in edges:
        adj[e['source']].append(e['target'])

    visited = set()
    rec_stack = set()
    cycle_path = []

    def find_cycle(u, path):
        """DFS to find a cycle. Returns True if cycle found and sets cycle_path."""
        nonlocal cycle_path
        visited.add(u)
        rec_stack.add(u)
        path.append(u)
        
        for v in adj[u]:
            if v not in visited:
                if find_cycle(v, path):
                    return True
            elif v in rec_stack:
                # Cycle found: from current node back to v
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

    # Extract process IDs from cycle path
    processes_involved = [nid for nid in cycle_path 
                         if any(n['id'] == nid and n['type'] == 'process' for n in nodes)]

    return deadlock, processes_involved, cycle_path


def recover_deadlock(allocation, available, deadlocked_processes, strategy):
    """
    Deadlock Recovery with 3 strategies.
    
    Args:
        allocation: 2D list of resource allocations [process_index][resource_index]
        available: List of available resources [resource_index]
        deadlocked_processes: List of process IDs in deadlock (e.g., ['P0', 'P1'])
        strategy: One of 'terminate-all', 'terminate-one-by-one', or 'preemption'
    
    Returns:
        (strategy_used, steps, updated_allocation)
        - strategy_used: The strategy selected
        - steps: List of step descriptions
        - updated_allocation: Updated allocation matrix
    """
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
        # Terminate processes in order of resource usage (highest first)
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
                    all(current_alloc[int(p.replace('P', ''))][j] <= current_avail[j] 
                        for j in range(num_resources))
                    for p in remaining
                )
                if can_proceed:
                    steps.append(f"Deadlock resolved! Remaining processes [{', '.join(remaining)}] can now proceed.")
                    break

    return strategy, steps, current_alloc
