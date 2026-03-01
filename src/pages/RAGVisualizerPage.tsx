import React, { useState, useRef, useCallback, useMemo } from 'react';
import ReactFlow, {
    ReactFlowProvider,
    addEdge,
    useNodesState,
    useEdgesState,
    Controls,
    Background,
    Connection,
    Edge,
    Node,
    MarkerType,
    MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { ProcessNode, ResourceNode } from '../components/rag-visualizer/CustomNodes';
import { detectDeadlock } from '../lib/ragEngine';
import { DeadlockReport } from '../lib/ragTypes';
import {
    Box, Layers, GripVertical, PlayCircle, CheckCircle,
    Play, RotateCcw, Activity, AlertTriangle, CheckCircle2
} from 'lucide-react';
import { cn } from '../lib/utils';

// ─── Initial nodes for the canvas ─────────────────────────────────────
const initialNodes: Node[] = [
    { id: 'p1', type: 'process', position: { x: 250, y: 100 }, data: { label: 'Process 1', pid: 'P1' } },
    { id: 'r1', type: 'resource', position: { x: 250, y: 300 }, data: { label: 'Resource 1', rid: 'R1', instances: 1 } },
];
const initialEdges: Edge[] = [];

let id = 0;
const getId = () => `node_${id++}_${Date.now()}`;

// ═══════════════════════════════════════════════════════════════════════
// Sidebar — drag & drop library + sample scenarios
// ═══════════════════════════════════════════════════════════════════════
interface RAGSidebarProps {
    onLoadSample: () => void;
    onLoadSafeCase: () => void;
}

const RAGSidebar: React.FC<RAGSidebarProps> = ({ onLoadSample, onLoadSafeCase }) => {
    const onDragStart = (event: React.DragEvent, nodeType: string) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.effectAllowed = 'move';
    };

    return (
        <aside className="w-64 bg-stone-50 border-r border-stone-200 flex flex-col h-full overflow-y-auto">
            <div className="p-4">
                <h2 className="text-[10px] font-bold text-stone-400 mb-4 uppercase tracking-widest">Node Library</h2>

                <div className="space-y-2">
                    <div
                        className="group flex items-center gap-3 p-3 bg-white border border-stone-200 rounded-lg cursor-move hover:bg-stone-50 hover:border-stone-300 hover:shadow-sm transition-all"
                        onDragStart={(event) => onDragStart(event, 'process')}
                        draggable
                    >
                        <GripVertical size={16} className="text-stone-300 group-hover:text-stone-500" />
                        <div className="p-1.5 bg-blue-50 rounded-lg text-blue-500">
                            <Box size={16} />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-stone-700">Process</p>
                            <p className="text-[10px] text-stone-400">Active entity</p>
                        </div>
                    </div>

                    <div
                        className="group flex items-center gap-3 p-3 bg-white border border-stone-200 rounded-lg cursor-move hover:bg-stone-50 hover:border-stone-300 hover:shadow-sm transition-all"
                        onDragStart={(event) => onDragStart(event, 'resource')}
                        draggable
                    >
                        <GripVertical size={16} className="text-stone-300 group-hover:text-stone-500" />
                        <div className="p-1.5 bg-emerald-50 rounded-lg text-emerald-500">
                            <Layers size={16} />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-stone-700">Resource</p>
                            <p className="text-[10px] text-stone-400">Allocatable item</p>
                        </div>
                    </div>
                </div>

                <div className="mt-8">
                    <h2 className="text-[10px] font-bold text-stone-400 mb-3 uppercase tracking-widest">Scenarios</h2>
                    <div className="space-y-2">
                        <button
                            onClick={onLoadSample}
                            className="w-full flex items-center gap-2.5 p-3 text-sm text-stone-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 hover:border-red-300 transition-all text-left"
                        >
                            <PlayCircle size={16} className="text-red-500" />
                            <span>Load Deadlock Scenario</span>
                        </button>
                        <button
                            onClick={onLoadSafeCase}
                            className="w-full flex items-center gap-2.5 p-3 text-sm text-stone-600 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 hover:border-emerald-300 transition-all text-left"
                        >
                            <CheckCircle size={16} className="text-emerald-500" />
                            <span>Load Safe Scenario</span>
                        </button>
                    </div>
                </div>

                <div className="mt-8">
                    <h2 className="text-[10px] font-bold text-stone-400 mb-3 uppercase tracking-widest">Instructions</h2>
                    <div className="space-y-2 text-xs text-stone-500 leading-relaxed">
                        <p><span className="text-stone-700 font-medium">1.</span> Drag nodes from library above onto the canvas.</p>
                        <p><span className="text-stone-700 font-medium">2.</span> Connect handles to create edges.</p>
                        <p><span className="text-stone-700 font-medium">3.</span> <span className="text-blue-600">Process → Resource</span> = Request</p>
                        <p><span className="text-stone-700 font-medium">4.</span> <span className="text-emerald-600">Resource → Process</span> = Allocation</p>
                        <p><span className="text-stone-700 font-medium">5.</span> Select nodes to edit properties in the inspector.</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

// ═══════════════════════════════════════════════════════════════════════
// Inspector — simulation controls + property editor
// ═══════════════════════════════════════════════════════════════════════
interface RAGInspectorProps {
    selectedNode: Node | null;
    onUpdateNode: (id: string, data: any) => void;
    report: DeadlockReport | null;
    onRunSimulation: () => void;
    onReset: () => void;
}

const RAGInspector: React.FC<RAGInspectorProps> = ({
    selectedNode,
    onUpdateNode,
    report,
    onRunSimulation,
    onReset
}) => {
    return (
        <aside className="w-80 bg-stone-50 border-l border-stone-200 flex flex-col h-full overflow-y-auto">
            {/* Simulation Control Header */}
            <div className="p-4 border-b border-stone-200">
                <h2 className="text-[10px] font-bold text-stone-400 mb-3 uppercase tracking-widest">Simulation</h2>
                <div className="flex gap-2">
                    <button
                        onClick={onRunSimulation}
                        className="flex-1 flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white py-2.5 px-3 rounded-lg transition-all text-sm font-bold shadow-sm"
                    >
                        <Play size={14} /> Run Check
                    </button>
                    <button
                        onClick={onReset}
                        className="flex items-center justify-center gap-2 bg-stone-100 text-stone-600 py-2.5 px-3 rounded-lg hover:bg-stone-200 transition-all border border-stone-200"
                        title="Reset Deadlock State"
                    >
                        <RotateCcw size={14} />
                    </button>
                </div>
            </div>

            {/* Report Panel */}
            {report && (
                <div className="p-4 border-b border-stone-200">
                    <h3 className="text-[10px] font-bold text-stone-400 mb-3 uppercase tracking-widest">Analysis Result</h3>
                    {report.isDeadlocked ? (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex items-start gap-2.5 text-red-700 font-bold text-sm">
                                <AlertTriangle size={16} className="mt-0.5" />
                                Deadlock Detected!
                            </div>
                            <p className="text-xs text-red-600/70 mt-2">
                                Cycle found involving: {report.deadlockedProcessIds.join(', ')}
                            </p>
                            {report.cycles.length > 0 && (
                                <div className="mt-3 text-[11px] font-mono bg-stone-800 px-3 py-2 rounded-lg text-red-300 border border-stone-700">
                                    {report.cycles[0].join(' → ')}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                            <div className="flex items-center gap-2.5 text-emerald-700 font-bold text-sm">
                                <CheckCircle2 size={16} />
                                System Safe
                            </div>
                            <p className="text-xs text-emerald-600/70 mt-2">
                                No circular wait detected. Safe sequence found.
                            </p>
                        </div>
                    )}

                    <div className="mt-3 space-y-1">
                        {report.log.map((l, i) => (
                            <div key={i} className={cn(
                                "text-[10px] font-mono border-l-2 pl-2 py-0.5",
                                l.type === 'error' ? "border-red-300 text-red-500" :
                                    l.type === 'success' ? "border-emerald-300 text-emerald-600" :
                                        "border-stone-200 text-stone-500"
                            )}>
                                {l.message}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Properties Editor */}
            <div className="p-4 flex-1">
                <h2 className="text-[10px] font-bold text-stone-400 mb-4 uppercase tracking-widest">Properties</h2>

                {selectedNode ? (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-stone-500 mb-1.5">Label</label>
                            <input
                                type="text"
                                value={selectedNode.data.label}
                                onChange={(e) => onUpdateNode(selectedNode.id, { label: e.target.value })}
                                className="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm text-stone-800 focus:outline-none focus:ring-1 focus:ring-orange-200 focus:border-orange-300"
                            />
                        </div>

                        {selectedNode.type === 'process' && (
                            <div>
                                <label className="block text-xs font-medium text-stone-500 mb-1.5">Process ID (PID)</label>
                                <input
                                    type="text"
                                    value={selectedNode.data.pid}
                                    onChange={(e) => onUpdateNode(selectedNode.id, { pid: e.target.value })}
                                    className="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm text-stone-800 focus:outline-none focus:ring-1 focus:ring-orange-200 focus:border-orange-300"
                                />
                            </div>
                        )}

                        {selectedNode.type === 'resource' && (
                            <div>
                                <label className="block text-xs font-medium text-stone-500 mb-1.5">Instances</label>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => onUpdateNode(selectedNode.id, { instances: Math.max(1, selectedNode.data.instances - 1) })}
                                        className="w-9 h-9 flex items-center justify-center bg-white rounded-lg hover:bg-stone-100 text-stone-700 border border-stone-200 transition-colors font-bold"
                                    >-</button>
                                    <span className="flex-1 text-center font-mono text-sm text-stone-800">{selectedNode.data.instances}</span>
                                    <button
                                        onClick={() => onUpdateNode(selectedNode.id, { instances: selectedNode.data.instances + 1 })}
                                        className="w-9 h-9 flex items-center justify-center bg-white rounded-lg hover:bg-stone-100 text-stone-700 border border-stone-200 transition-colors font-bold"
                                    >+</button>
                                </div>
                            </div>
                        )}

                        <div className="pt-4 border-t border-stone-200 space-y-1">
                            <div className="text-[10px] text-stone-400 font-mono">ID: {selectedNode.id}</div>
                            <div className="text-[10px] text-stone-400 font-mono">Pos: {Math.round(selectedNode.position.x)}, {Math.round(selectedNode.position.y)}</div>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-40 text-stone-400 text-center">
                        <Activity size={32} className="mb-2 opacity-30" />
                        <p className="text-sm text-stone-400">Select a node to edit properties</p>
                    </div>
                )}
            </div>
        </aside>
    );
};

// ═══════════════════════════════════════════════════════════════════════
// Main RAG Visualizer Page Content
// ═══════════════════════════════════════════════════════════════════════
const RAGContent = () => {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    const [report, setReport] = useState<DeadlockReport | null>(null);

    const nodeTypes = useMemo(() => ({
        process: ProcessNode,
        resource: ResourceNode,
    }), []);

    // Handle connection logic with validation
    const onConnect = useCallback(
        (params: Connection) => {
            const sourceNode = nodes.find((n) => n.id === params.source);
            const targetNode = nodes.find((n) => n.id === params.target);

            if (!sourceNode || !targetNode) return;

            if (sourceNode.type === targetNode.type) {
                alert("You must connect a Process to a Resource (Request) or a Resource to a Process (Allocation).");
                return;
            }

            const isAllocation = sourceNode.type === 'resource';

            const newEdge: Edge = {
                ...params,
                id: `e_${params.source}_${params.target}_${Date.now()}`,
                type: 'default',
                animated: !isAllocation,
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: isAllocation ? '#10b981' : '#3b82f6',
                },
                style: {
                    stroke: isAllocation ? '#10b981' : '#3b82f6',
                    strokeWidth: 2,
                    strokeDasharray: isAllocation ? '0' : '5 5',
                },
            };

            setEdges((eds) => addEdge(newEdge, eds));
            setReport(null);
        },
        [nodes, setEdges]
    );

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();
            const type = event.dataTransfer.getData('application/reactflow');
            if (typeof type === 'undefined' || !type) return;

            const position = reactFlowInstance.screenToFlowPosition({
                x: event.clientX,
                y: event.clientY,
            });

            const newNode: Node = {
                id: getId(),
                type,
                position,
                data: {
                    label: type === 'process' ? `New Process` : `New Resource`,
                    pid: type === 'process' ? `P${Math.floor(Math.random() * 1000)}` : undefined,
                    rid: type === 'resource' ? `R${Math.floor(Math.random() * 1000)}` : undefined,
                    instances: type === 'resource' ? 1 : undefined
                },
            };

            setNodes((nds) => nds.concat(newNode));
            setReport(null);
        },
        [reactFlowInstance, setNodes]
    );

    const onSelectionChange = useCallback(({ nodes: selectedNodes }: { nodes: Node[] }) => {
        if (selectedNodes.length > 0) {
            setSelectedNodeId(selectedNodes[0].id);
        } else {
            setSelectedNodeId(null);
        }
    }, []);

    const onUpdateNode = (id: string, data: any) => {
        setNodes((nds) =>
            nds.map((node) => {
                if (node.id === id) {
                    return { ...node, data: { ...node.data, ...data } };
                }
                return node;
            })
        );
        setReport(null);
    };

    const handleRunSimulation = () => {
        const result = detectDeadlock(nodes, edges);
        setReport(result);

        setNodes((nds) => nds.map(node => {
            const isDeadlocked =
                result.deadlockedProcessIds.includes(node.id) ||
                result.deadlockedResourceIds.includes(node.id);
            return {
                ...node,
                data: { ...node.data, isDeadlocked }
            };
        }));

        if (result.isDeadlocked && result.cycles.length > 0) {
            const cycleNodes = new Set(result.cycles[0]);
            setEdges(eds => eds.map(edge => {
                const isCycleEdge = cycleNodes.has(edge.source) && cycleNodes.has(edge.target);
                return {
                    ...edge,
                    style: {
                        ...edge.style,
                        stroke: isCycleEdge ? '#EF4444' : (edge.style?.stroke || '#3b82f6'),
                        strokeWidth: isCycleEdge ? 3 : 2
                    },
                    animated: isCycleEdge ? true : edge.animated
                };
            }));
        }
    };

    const handleReset = () => {
        setReport(null);
        setNodes(nds => nds.map(n => ({
            ...n,
            data: { ...n.data, isDeadlocked: false }
        })));
        setEdges(eds => eds.map(e => {
            const sourceNode = nodes.find(n => n.id === e.source);
            const isAllocation = sourceNode?.type === 'resource';
            return {
                ...e,
                animated: !isAllocation,
                style: {
                    ...e.style,
                    stroke: isAllocation ? '#10b981' : '#3b82f6',
                    strokeWidth: 2
                }
            };
        }));
    };

    const handleLoadSample = () => {
        const p1Id = 'p_sample_1';
        const p2Id = 'p_sample_2';
        const r1Id = 'r_sample_1';
        const r2Id = 'r_sample_2';

        const newNodes: Node[] = [
            { id: p1Id, type: 'process', position: { x: 100, y: 200 }, data: { label: 'Process A', pid: 'P1' } },
            { id: p2Id, type: 'process', position: { x: 400, y: 200 }, data: { label: 'Process B', pid: 'P2' } },
            { id: r1Id, type: 'resource', position: { x: 250, y: 50 }, data: { label: 'Resource X', rid: 'RX', instances: 1 } },
            { id: r2Id, type: 'resource', position: { x: 250, y: 350 }, data: { label: 'Resource Y', rid: 'RY', instances: 1 } },
        ];

        const newEdges: Edge[] = [
            {
                id: 'e_s1', source: p1Id, target: r1Id,
                type: 'default', animated: true,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
                style: { stroke: '#3b82f6', strokeWidth: 2, strokeDasharray: '5 5' }
            },
            {
                id: 'e_s2', source: r1Id, target: p2Id,
                type: 'default', animated: false,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
                style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '0' }
            },
            {
                id: 'e_s3', source: p2Id, target: r2Id,
                type: 'default', animated: true,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
                style: { stroke: '#3b82f6', strokeWidth: 2, strokeDasharray: '5 5' }
            },
            {
                id: 'e_s4', source: r2Id, target: p1Id,
                type: 'default', animated: false,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
                style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '0' }
            },
        ];

        setNodes(newNodes);
        setEdges(newEdges);
        setReport(null);
        setTimeout(() => reactFlowInstance?.fitView({ padding: 0.2 }), 100);
    };

    const handleLoadSafeCase = () => {
        const p1Id = 'p_safe_1';
        const p2Id = 'p_safe_2';
        const p3Id = 'p_safe_3';
        const r1Id = 'r_safe_1';
        const r2Id = 'r_safe_2';

        const newNodes: Node[] = [
            { id: p1Id, type: 'process', position: { x: 100, y: 100 }, data: { label: 'Process P1', pid: 'P1' } },
            { id: p2Id, type: 'process', position: { x: 100, y: 250 }, data: { label: 'Process P2', pid: 'P2' } },
            { id: p3Id, type: 'process', position: { x: 100, y: 400 }, data: { label: 'Process P3', pid: 'P3' } },
            { id: r1Id, type: 'resource', position: { x: 400, y: 150 }, data: { label: 'Resource R1', rid: 'R1', instances: 1 } },
            { id: r2Id, type: 'resource', position: { x: 400, y: 350 }, data: { label: 'Resource R2', rid: 'R2', instances: 1 } },
        ];

        const newEdges: Edge[] = [
            {
                id: 'e_safe1', source: r1Id, target: p1Id,
                type: 'default', animated: false,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
                style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '0' }
            },
            {
                id: 'e_safe2', source: p2Id, target: r1Id,
                type: 'default', animated: true,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
                style: { stroke: '#3b82f6', strokeWidth: 2, strokeDasharray: '5 5' }
            },
            {
                id: 'e_safe3', source: p2Id, target: r2Id,
                type: 'default', animated: true,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
                style: { stroke: '#3b82f6', strokeWidth: 2, strokeDasharray: '5 5' }
            },
            {
                id: 'e_safe4', source: p3Id, target: r2Id,
                type: 'default', animated: true,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
                style: { stroke: '#3b82f6', strokeWidth: 2, strokeDasharray: '5 5' }
            },
        ];

        setNodes(newNodes);
        setEdges(newEdges);
        setReport(null);
        setTimeout(() => reactFlowInstance?.fitView({ padding: 0.2 }), 100);
    };

    const selectedNode = nodes.find((n) => n.id === selectedNodeId) || null;

    return (
        <div className="flex h-full w-full">
            <RAGSidebar onLoadSample={handleLoadSample} onLoadSafeCase={handleLoadSafeCase} />
            <div className="flex-1 h-full relative" ref={reactFlowWrapper}>
                <div className="absolute top-4 left-4 z-10 bg-white/80 backdrop-blur border border-stone-200 px-3 py-1.5 rounded-lg shadow-sm text-xs text-stone-500">
                    RAG Visualizer — Interactive Deadlock Detection
                </div>
                <div className="absolute top-4 right-4 z-10 flex gap-3 text-xs">
                    <div className="flex items-center gap-2 bg-white/80 backdrop-blur border border-stone-200 rounded-lg px-3 py-1.5 shadow-sm">
                        <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                        <span className="text-stone-500">Process</span>
                    </div>
                    <div className="flex items-center gap-2 bg-white/80 backdrop-blur border border-stone-200 rounded-lg px-3 py-1.5 shadow-sm">
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                        <span className="text-stone-500">Resource</span>
                    </div>
                    <div className="flex items-center gap-2 bg-white/80 backdrop-blur border border-stone-200 rounded-lg px-3 py-1.5 shadow-sm">
                        <div className="w-1.5 h-[10px] border border-dashed border-blue-400 rounded-sm" />
                        <span className="text-stone-500">Request</span>
                    </div>
                    <div className="flex items-center gap-2 bg-white/80 backdrop-blur border border-stone-200 rounded-lg px-3 py-1.5 shadow-sm">
                        <div className="w-4 h-0.5 bg-emerald-500 rounded" />
                        <span className="text-stone-500">Allocation</span>
                    </div>
                </div>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onInit={setReactFlowInstance}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    onSelectionChange={onSelectionChange}
                    nodeTypes={nodeTypes}
                    fitView
                    className="!bg-stone-50"
                >
                    <Background color="#d6d3d1" gap={24} size={1} />
                    <Controls className="!bg-white !border-stone-200 !shadow-sm !rounded-lg [&>button]:!bg-white [&>button]:!border-stone-200 [&>button:hover]:!bg-stone-50 [&>button]:!text-stone-500 [&>button]:!rounded-lg" />
                    <MiniMap
                        className="!bg-white !border-stone-200 !rounded-lg !shadow-sm"
                        nodeColor={(node) => {
                            if (node.data?.isDeadlocked) return '#EF4444';
                            return node.type === 'process' ? '#3b82f6' : '#10b981';
                        }}
                        maskColor="rgba(245, 245, 244, 0.7)"
                    />
                </ReactFlow>
            </div>
            <RAGInspector
                selectedNode={selectedNode}
                onUpdateNode={onUpdateNode}
                report={report}
                onRunSimulation={handleRunSimulation}
                onReset={handleReset}
            />
        </div>
    );
};

// ═══════════════════════════════════════════════════════════════════════
// Exported Page Component
// ═══════════════════════════════════════════════════════════════════════
const RAGVisualizerPage = () => {
    return (
        <div className="h-screen -m-0">
            <ReactFlowProvider>
                <RAGContent />
            </ReactFlowProvider>
        </div>
    );
};

export default RAGVisualizerPage;
