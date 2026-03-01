import React, { useState } from 'react';
import { Search, AlertTriangle, CheckCircle2, Plus, Trash2, RotateCcw } from 'lucide-react';
import RAG from '../components/RAG';
import { cn } from '../lib/utils';

const presets = {
  deadlock: {
    name: 'Deadlock Scenario',
    nodes: [
      { id: 'P1', type: 'process' as const },
      { id: 'P2', type: 'process' as const },
      { id: 'P3', type: 'process' as const },
      { id: 'R1', type: 'resource' as const },
      { id: 'R2', type: 'resource' as const },
    ],
    edges: [
      { source: 'P1', target: 'R1' },
      { source: 'R1', target: 'P2' },
      { source: 'P2', target: 'R2' },
      { source: 'R2', target: 'P1' },
      { source: 'P3', target: 'R2' },
    ],
  },
  safe: {
    name: 'Safe Scenario',
    nodes: [
      { id: 'P1', type: 'process' as const },
      { id: 'P2', type: 'process' as const },
      { id: 'R1', type: 'resource' as const },
      { id: 'R2', type: 'resource' as const },
    ],
    edges: [
      { source: 'P1', target: 'R1' },
      { source: 'R2', target: 'P2' },
    ],
  },
  complex: {
    name: 'Complex Deadlock',
    nodes: [
      { id: 'P1', type: 'process' as const },
      { id: 'P2', type: 'process' as const },
      { id: 'P3', type: 'process' as const },
      { id: 'R1', type: 'resource' as const },
      { id: 'R2', type: 'resource' as const },
      { id: 'R3', type: 'resource' as const },
    ],
    edges: [
      { source: 'P1', target: 'R1' },
      { source: 'R1', target: 'P2' },
      { source: 'P2', target: 'R2' },
      { source: 'R2', target: 'P3' },
      { source: 'P3', target: 'R3' },
      { source: 'R3', target: 'P1' },
    ],
  },
};

const DetectionPage = () => {
  const [nodes, setNodes] = useState<any[]>(presets.deadlock.nodes);
  const [edges, setEdges] = useState<any[]>(presets.deadlock.edges);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [edgeFrom, setEdgeFrom] = useState('');
  const [edgeTo, setEdgeTo] = useState('');

  const handleDetect = async () => {
    setLoading(true);
    try {
      // D3 mutates nodes/edges with position data and converts source/target
      // from strings to object references. Clean before sending to API.
      const cleanNodes = nodes.map((n: any) => ({ id: n.id, type: n.type }));
      const cleanEdges = edges.map((e: any) => ({
        source: typeof e.source === 'string' ? e.source : e.source.id,
        target: typeof e.target === 'string' ? e.target : e.target.id,
      }));
      const response = await fetch('/api/deadlock/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes: cleanNodes, edges: cleanEdges })
      });
      const data = await response.json();
      // Sanitize: ensure cycle_path and processes_involved are string arrays
      if (data.cycle_path) {
        data.cycle_path = data.cycle_path.map((item: any) =>
          typeof item === 'string' ? item : (item?.id || String(item))
        );
      }
      if (data.processes_involved) {
        data.processes_involved = data.processes_involved.map((item: any) =>
          typeof item === 'string' ? item : (item?.id || String(item))
        );
      }
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddEdge = () => {
    if (!edgeFrom.trim() || !edgeTo.trim()) return;
    const from = edgeFrom.trim().toUpperCase();
    const to = edgeTo.trim().toUpperCase();

    const newNodes = [...nodes];
    if (!newNodes.find((n: any) => n.id === from)) {
      newNodes.push({ id: from, type: from.startsWith('P') ? 'process' : 'resource' });
    }
    if (!newNodes.find((n: any) => n.id === to)) {
      newNodes.push({ id: to, type: to.startsWith('P') ? 'process' : 'resource' });
    }
    setNodes(newNodes);
    setEdges([...edges, { source: from, target: to }]);
    setEdgeFrom('');
    setEdgeTo('');
    setResult(null);
  };

  const handleRemoveEdge = (index: number) => {
    const newEdges = edges.filter((_, i) => i !== index);
    setEdges(newEdges);
    setResult(null);
  };

  const loadPreset = (preset: keyof typeof presets) => {
    setNodes([...presets[preset].nodes]);
    setEdges([...presets[preset].edges]);
    setResult(null);
  };

  const clearGraph = () => {
    setNodes([]);
    setEdges([]);
    setResult(null);
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Deadlock Detection</h2>
          <p className="text-slate-400">Cycle detection in Resource Allocation Graphs (RAG)</p>
        </div>
        <button
          onClick={handleDetect}
          disabled={loading || nodes.length === 0}
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-900/20 disabled:opacity-50"
        >
          <Search className="w-5 h-5" />
          {loading ? 'Scanning...' : 'Detect Deadlock'}
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-6">
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">Resource Allocation Graph</h3>
              <div className="flex gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span className="text-slate-400">Process</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-slate-400">Resource</span>
                </div>
              </div>
            </div>

            <RAG
              nodes={nodes}
              edges={edges}
              highlightPath={result?.cycle_path || []}
            />
          </div>
        </div>

        <div className="space-y-6">
          {result ? (
            <div className={cn(
              "rounded-2xl p-6 border transition-all",
              result.deadlock ? "bg-red-500/10 border-red-500/20" : "bg-emerald-500/10 border-emerald-500/20"
            )}>
              <div className="flex items-center gap-3 mb-4">
                {result.deadlock ? (
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                ) : (
                  <CheckCircle2 className="w-8 h-8 text-emerald-500" />
                )}
                <h3 className={cn(
                  "text-xl font-bold",
                  result.deadlock ? "text-red-400" : "text-emerald-400"
                )}>
                  {result.deadlock ? 'Deadlock Detected!' : 'No Deadlock Found'}
                </h3>
              </div>

              {result.deadlock && (
                <div className="space-y-4">
                  <div className="bg-slate-950/50 rounded-xl p-4">
                    <p className="text-xs text-slate-500 uppercase font-bold mb-2">Cycle Path</p>
                    <div className="flex flex-wrap gap-2">
                      {result.cycle_path.map((id: string, i: number) => (
                        <React.Fragment key={`${id}-${i}`}>
                          <span className={cn(
                            "px-2 py-1 rounded text-xs font-mono",
                            id.startsWith('P') ? "bg-blue-500/20 text-blue-400" : "bg-emerald-500/20 text-emerald-400"
                          )}>
                            {id}
                          </span>
                          {i < result.cycle_path.length - 1 && (
                            <span className="text-slate-600">→</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>

                  <div className="bg-slate-950/50 rounded-xl p-4">
                    <p className="text-xs text-slate-500 uppercase font-bold mb-2">Processes Involved</p>
                    <div className="flex gap-2">
                      {result.processes_involved.map((p: string) => (
                        <span key={p} className="bg-red-500/20 text-red-400 px-3 py-1 rounded-lg text-sm font-bold border border-red-500/20">
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {!result.deadlock && (
                <p className="text-slate-400 text-sm">
                  No cycles were found in the Resource Allocation Graph. The system is currently free from deadlock.
                </p>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-slate-900/20 border border-dashed border-white/10 rounded-2xl min-h-[200px]">
              <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
                <Search className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="text-lg font-medium text-slate-400">Scan Required</h3>
              <p className="text-sm text-slate-500 max-w-xs mt-2">
                Click the detect button to analyze the current graph for potential deadlocks.
              </p>
            </div>
          )}

          {/* Presets */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Presets</h3>
            <div className="space-y-2">
              {Object.entries(presets).map(([key, preset]) => (
                <button
                  key={key}
                  onClick={() => loadPreset(key as keyof typeof presets)}
                  className="w-full text-left px-4 py-3 bg-slate-800/50 border border-white/5 rounded-xl hover:border-white/20 text-sm text-slate-300 transition-all"
                >
                  {preset.name}
                  <span className="text-xs text-slate-600 ml-2">({preset.nodes.length} nodes, {preset.edges.length} edges)</span>
                </button>
              ))}
              <button
                onClick={clearGraph}
                className="w-full text-left px-4 py-3 bg-red-500/5 border border-red-500/10 rounded-xl hover:border-red-500/30 text-sm text-red-400 transition-all flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" /> Clear Graph
              </button>
            </div>
          </div>

          {/* Edge Management */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Edge Management</h3>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-slate-500 uppercase font-bold mb-2">Add Edge</p>
                <div className="flex gap-2">
                  <input
                    placeholder="From (P1)"
                    value={edgeFrom}
                    onChange={(e) => setEdgeFrom(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddEdge()}
                    className="w-full bg-slate-800 border border-white/10 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                  <input
                    placeholder="To (R1)"
                    value={edgeTo}
                    onChange={(e) => setEdgeTo(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddEdge()}
                    className="w-full bg-slate-800 border border-white/10 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                  <button onClick={handleAddEdge} className="bg-slate-700 hover:bg-slate-600 p-2 rounded text-white transition-colors">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {edges.length > 0 && (
                <div>
                  <p className="text-xs text-slate-500 uppercase font-bold mb-2">Current Edges</p>
                  <div className="space-y-1 max-h-[200px] overflow-y-auto">
                    {edges.map((edge, i) => (
                      <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded-lg px-3 py-2 group">
                        <span className="text-xs font-mono text-slate-400">
                          {edge.source} → {edge.target}
                        </span>
                        <button
                          onClick={() => handleRemoveEdge(i)}
                          className="text-slate-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-[10px] text-slate-500 italic">
                P→R = Request edge. R→P = Assignment edge. Nodes auto-created.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetectionPage;
