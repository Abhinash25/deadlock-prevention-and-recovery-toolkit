import { Edge, Node } from 'reactflow';

export type RAGNodeType = 'process' | 'resource';

export interface ProcessData {
  label: string;
  pid: string;
  isDeadlocked?: boolean;
}

export interface ResourceData {
  label: string;
  rid: string;
  instances: number;
  available?: number;
  isDeadlocked?: boolean;
}

export interface SimulationStep {
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
  timestamp: number;
}

export interface DeadlockReport {
  isDeadlocked: boolean;
  deadlockedProcessIds: string[];
  deadlockedResourceIds: string[];
  cycles: string[][];
  log: SimulationStep[];
}

export type AppNode = Node<ProcessData | ResourceData>;
export type AppEdge = Edge;
