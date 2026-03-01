export interface BankersInput {
  processes: string[];
  resources: string[];
  allocation: number[][];
  max: number[][];
  available: number[];
}

export interface DeadlockInput {
  nodes: { id: string; type: 'process' | 'resource' }[];
  edges: { source: string; target: string }[];
}

export interface RecoveryInput {
  allocation: number[][];
  available: number[];
  deadlockedProcesses: string[];
  strategy: 'terminate-all' | 'terminate-one-by-one' | 'preemption';
}

/**
 * Banker's Algorithm implementation
 */
export function bankersSafetyCheck(input: BankersInput) {
  const { processes, resources, allocation, max, available } = input;
  const n = processes.length;
  const m = resources.length;

  const need = max.map((row, i) => row.map((val, j) => val - allocation[i][j]));
  const work = [...available];
  const finish = new Array(n).fill(false);
  const safeSequence: string[] = [];
  const log: string[] = [];

  log.push(`Initial Work: [${work.join(', ')}]`);

  let count = 0;
  while (count < n) {
    let found = false;
    for (let i = 0; i < n; i++) {
      if (!finish[i]) {
        let j;
        for (j = 0; j < m; j++) {
          if (need[i][j] > work[j]) break;
        }

        if (j === m) {
          log.push(`Process ${processes[i]} can be allocated resources. Need: [${need[i].join(', ')}] <= Work: [${work.join(', ')}]`);
          for (let k = 0; k < m; k++) {
            work[k] += allocation[i][k];
          }
          finish[i] = true;
          safeSequence.push(processes[i]);
          log.push(`Process ${processes[i]} finished. New Work: [${work.join(', ')}]`);
          found = true;
          count++;
        }
      }
    }

    if (!found) {
      log.push("System is in an UNSAFE state. No process can proceed.");
      return {
        safe: false,
        safe_sequence: [],
        need_matrix: need,
        log
      };
    }
  }

  log.push("System is in a SAFE state.");
  return {
    safe: true,
    safe_sequence: safeSequence,
    need_matrix: need,
    log
  };
}

/**
 * Deadlock Detection using DFS for cycle detection in RAG
 */
export function detectDeadlock(input: DeadlockInput) {
  const { nodes, edges } = input;
  const adj: Record<string, string[]> = {};
  nodes.forEach(node => adj[node.id] = []);
  edges.forEach(edge => adj[edge.source].push(edge.target));

  const visited = new Set<string>();
  const recStack = new Set<string>();
  let cyclePath: string[] = [];

  function findCycle(u: string, path: string[]): boolean {
    visited.add(u);
    recStack.add(u);
    path.push(u);

    for (const v of adj[u]) {
      if (!visited.has(v)) {
        if (findCycle(v, path)) return true;
      } else if (recStack.has(v)) {
        // Cycle found
        const cycleStartIdx = path.indexOf(v);
        cyclePath = path.slice(cycleStartIdx);
        return true;
      }
    }

    recStack.delete(u);
    path.pop();
    return false;
  }

  let deadlock = false;
  for (const node of nodes) {
    if (!visited.has(node.id)) {
      if (findCycle(node.id, [])) {
        deadlock = true;
        break;
      }
    }
  }

  const processesInvolved = cyclePath.filter(id => {
    const node = nodes.find(n => n.id === id);
    return node?.type === 'process';
  });

  return {
    deadlock,
    processes_involved: processesInvolved,
    cycle_path: cyclePath,
    graph_data: { nodes, edges }
  };
}

/**
 * Deadlock Recovery implementation
 */
export function recoverDeadlock(input: RecoveryInput) {
  const { allocation, available, deadlockedProcesses, strategy } = input;
  const steps: string[] = [];
  let currentAllocation = allocation.map(row => [...row]);
  let currentAvailable = [...available];

  if (strategy === 'terminate-all') {
    steps.push(`Terminating all deadlocked processes: ${deadlockedProcesses.join(', ')}`);
    deadlockedProcesses.forEach(pId => {
      const pIdx = parseInt(pId.replace('P', ''));
      for (let j = 0; j < currentAvailable.length; j++) {
        currentAvailable[j] += currentAllocation[pIdx][j];
        currentAllocation[pIdx][j] = 0;
      }
      steps.push(`Process ${pId} terminated. Resources released.`);
    });
  } else if (strategy === 'terminate-one-by-one') {
    // Simple heuristic: terminate process with most resources first to recover faster
    const sorted = [...deadlockedProcesses].sort((a, b) => {
      const idxA = parseInt(a.replace('P', ''));
      const idxB = parseInt(b.replace('P', ''));
      const sumA = currentAllocation[idxA].reduce((s, v) => s + v, 0);
      const sumB = currentAllocation[idxB].reduce((s, v) => s + v, 0);
      return sumB - sumA;
    });

    for (const pId of sorted) {
      steps.push(`Terminating process ${pId} (one-by-one strategy).`);
      const pIdx = parseInt(pId.replace('P', ''));
      for (let j = 0; j < currentAvailable.length; j++) {
        currentAvailable[j] += currentAllocation[pIdx][j];
        currentAllocation[pIdx][j] = 0;
      }
      steps.push(`Process ${pId} terminated. Available resources: [${currentAvailable.join(', ')}]`);
    }
  } else if (strategy === 'preemption') {
    steps.push(`Attempting resource preemption from deadlocked processes: ${deadlockedProcesses.join(', ')}`);
    // Preempt resources one process at a time, releasing their held resources
    const remaining = [...deadlockedProcesses];
    while (remaining.length > 0) {
      // Pick process with fewest total resources (least disruption)
      remaining.sort((a, b) => {
        const idxA = parseInt(a.replace('P', ''));
        const idxB = parseInt(b.replace('P', ''));
        const sumA = currentAllocation[idxA].reduce((s, v) => s + v, 0);
        const sumB = currentAllocation[idxB].reduce((s, v) => s + v, 0);
        return sumA - sumB;
      });
      const victim = remaining.shift()!;
      const victimIdx = parseInt(victim.replace('P', ''));
      const preempted = [...currentAllocation[victimIdx]];
      for (let j = 0; j < currentAvailable.length; j++) {
        currentAvailable[j] += currentAllocation[victimIdx][j];
        currentAllocation[victimIdx][j] = 0;
      }
      steps.push(`Preempted resources [${preempted.join(', ')}] from process ${victim}. Available: [${currentAvailable.join(', ')}]`);
      steps.push(`Process ${victim} rolled back to a safe checkpoint.`);

      // Check if remaining processes can now proceed
      const canProceed = remaining.every(pId => {
        const pIdx = parseInt(pId.replace('P', ''));
        return currentAllocation[pIdx].every((val, j) => val <= currentAvailable[j]);
      });
      if (canProceed && remaining.length > 0) {
        steps.push(`Deadlock resolved! Remaining processes [${remaining.join(', ')}] can now proceed.`);
        break;
      }
    }
  }

  return {
    strategy_used: strategy,
    recovery_steps: steps,
    updated_allocation: currentAllocation,
    system_safe: true
  };
}

/**
 * Simulation Engine — runs a step-by-step resource allocation scenario
 * using the Banker's Algorithm to check safety at each step.
 */
export function runSimulation(input: any) {
  const numProcesses = input.numProcesses || 4;
  const numResources = input.numResources || 3;
  const log: string[] = [];

  // Generate initial system state
  const totalResources = Array.from({ length: numResources }, () => Math.floor(Math.random() * 8) + 4);
  const allocation: number[][] = Array.from({ length: numProcesses }, () =>
    Array.from({ length: numResources }, () => 0)
  );
  const max: number[][] = Array.from({ length: numProcesses }, () =>
    totalResources.map(t => Math.floor(Math.random() * (t + 1)))
  );
  const available = [...totalResources];
  const processes = Array.from({ length: numProcesses }, (_, i) => `P${i}`);
  const resources = Array.from({ length: numResources }, (_, i) => String.fromCharCode(65 + i));

  log.push(`Starting simulation with ${numProcesses} processes and ${numResources} resources.`);
  log.push(`Total Resources: [${totalResources.join(', ')}]`);
  log.push(`Available: [${available.join(', ')}]`);

  // Simulate allocation steps
  let deadlockDetected = false;
  const steps = numProcesses * 2;
  for (let step = 0; step < steps; step++) {
    const pIdx = Math.floor(Math.random() * numProcesses);
    const rIdx = Math.floor(Math.random() * numResources);
    const need = max[pIdx][rIdx] - allocation[pIdx][rIdx];

    if (need > 0 && available[rIdx] > 0) {
      const amount = Math.min(need, available[rIdx], Math.ceil(Math.random() * 2));
      // Tentatively allocate
      allocation[pIdx][rIdx] += amount;
      available[rIdx] -= amount;

      // Check safety
      const safetyResult = bankersSafetyCheck({ processes, resources, allocation, max, available });
      if (safetyResult.safe) {
        log.push(`[Step ${step + 1}] Granted ${amount} unit(s) of ${resources[rIdx]} to ${processes[pIdx]}. System SAFE. Sequence: ${safetyResult.safe_sequence.join(' → ')}`);
      } else {
        // Rollback
        allocation[pIdx][rIdx] -= amount;
        available[rIdx] += amount;
        log.push(`[Step ${step + 1}] Denied ${amount} unit(s) of ${resources[rIdx]} to ${processes[pIdx]}. Would cause UNSAFE state — request blocked.`);
      }
    } else {
      log.push(`[Step ${step + 1}] ${processes[pIdx]} has no pending need for ${resources[rIdx]}, skipping.`);
    }
  }

  // Final check
  const finalResult = bankersSafetyCheck({ processes, resources, allocation, max, available });
  const status = finalResult.safe ? 'safe' : 'unsafe';
  log.push(`--- Simulation Complete ---`);
  log.push(`Final Available: [${available.join(', ')}]`);
  log.push(`Final Status: ${status.toUpperCase()}`);
  if (finalResult.safe) {
    log.push(`Safe Sequence: ${finalResult.safe_sequence.join(' → ')}`);
  }

  return {
    status,
    running_processes: processes.filter((_, i) => allocation[i].some(v => v > 0)),
    blocked_processes: finalResult.safe ? [] : processes,
    analysis_log: log
  };
}

