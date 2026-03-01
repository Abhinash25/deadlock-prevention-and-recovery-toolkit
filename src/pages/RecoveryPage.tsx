import React, { useState } from 'react';
import { RotateCcw, Zap, Trash2, ShieldAlert, CheckCircle2, Plus, X } from 'lucide-react';
import { cn } from '../lib/utils';
import { useSystem } from '../lib/SystemContext';

const RecoveryPage = () => {
  const { system } = useSystem();
  const [strategy, setStrategy] = useState<'terminate-all' | 'terminate-one-by-one' | 'preemption'>('terminate-one-by-one');
  const [deadlockedProcesses, setDeadlockedProcesses] = useState(['P0', 'P1']);
  const [numResources, setNumResources] = useState(3);
  const [allocation, setAllocation] = useState<number[][]>([[1, 0, 2], [0, 1, 0]]);
  const [available, setAvailable] = useState<number[]>([0, 0, 0]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [newProcessId, setNewProcessId] = useState('');

  const handleRecover = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/deadlock/recover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          allocation,
          available,
          deadlockedProcesses,
          strategy
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const addProcess = () => {
    if (!newProcessId.trim()) return;
    const id = newProcessId.trim().toUpperCase();
    if (deadlockedProcesses.includes(id)) return;
    setDeadlockedProcesses([...deadlockedProcesses, id]);
    setAllocation([...allocation, new Array(numResources).fill(0)]);
    setNewProcessId('');
    setResult(null);
  };

  const removeProcess = (index: number) => {
    setDeadlockedProcesses(deadlockedProcesses.filter((_, i) => i !== index));
    setAllocation(allocation.filter((_, i) => i !== index));
    setResult(null);
  };

  const updateAllocation = (r: number, c: number, val: string) => {
    const newAlloc = allocation.map((row, i) => i === r ? [...row] : row);
    newAlloc[r][c] = parseInt(val) || 0;
    setAllocation(newAlloc);
  };

  const resourceLabels = Array.from({ length: numResources }, (_, i) => String.fromCharCode(65 + i));

  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white">Deadlock Recovery</h2>
        <p className="text-slate-400">Strategies to break cycles and restore system safety</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">Select Strategy</h3>
            <div className="space-y-3">
              {[
                { id: 'terminate-all', name: 'Terminate All', icon: Trash2, desc: 'Stop all processes in the deadlock cycle simultaneously.' },
                { id: 'terminate-one-by-one', name: 'One-by-One', icon: Zap, desc: 'Terminate processes sequentially until cycle is broken.' },
                { id: 'preemption', name: 'Resource Preemption', icon: RotateCcw, desc: 'Take resources away from processes and give to others.' },
              ].map((s) => (
                <button
                  key={s.id}
                  onClick={() => setStrategy(s.id as any)}
                  className={cn(
                    "w-full text-left p-4 rounded-xl border transition-all group",
                    strategy === s.id
                      ? "bg-blue-600/10 border-blue-500/50 text-white"
                      : "bg-slate-800/50 border-white/5 text-slate-400 hover:border-white/20"
                  )}
                >
                  <div className="flex items-center gap-3 mb-1">
                    <s.icon className={cn(
                      "w-5 h-5",
                      strategy === s.id ? "text-blue-400" : "text-slate-500"
                    )} />
                    <span className="font-bold">{s.name}</span>
                  </div>
                  <p className="text-xs text-slate-500 group-hover:text-slate-400 transition-colors">
                    {s.desc}
                  </p>
                </button>
              ))}
            </div>

            <button
              onClick={handleRecover}
              disabled={loading || deadlockedProcesses.length === 0}
              className="w-full mt-8 bg-emerald-600 hover:bg-emerald-500 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-900/20 disabled:opacity-50"
            >
              <RotateCcw className="w-5 h-5" />
              {loading ? 'Executing...' : 'Execute Recovery'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {/* Deadlocked Processes Configuration */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Deadlocked Processes</h3>

            {/* Add process */}
            <div className="flex gap-2 mb-4">
              <input
                placeholder="Process ID (e.g. P3)"
                value={newProcessId}
                onChange={(e) => setNewProcessId(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addProcess()}
                className="flex-1 bg-slate-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
              <button onClick={addProcess} className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-bold text-sm flex items-center gap-1 transition-all">
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>

            {/* Process Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {deadlockedProcesses.map((p, idx) => (
                <div key={p} className="bg-slate-800 border border-white/5 rounded-xl p-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-red-500/20 rounded-lg flex items-center justify-center text-red-400 font-bold text-xs">
                      {p}
                    </div>
                    <div>
                      <span className="text-slate-300 font-medium text-sm">{p}</span>
                      <div className="text-[9px] text-red-400 uppercase font-bold">Blocked</div>
                    </div>
                  </div>
                  <button onClick={() => removeProcess(idx)} className="text-slate-600 hover:text-red-400 transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Allocation Matrix */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Allocation Matrix</h3>
              <div className="flex items-center gap-2">
                <label className="text-xs text-slate-500">Resources:</label>
                <input
                  type="number"
                  min={1}
                  max={6}
                  value={numResources}
                  onChange={(e) => {
                    const n = Math.max(1, Math.min(6, parseInt(e.target.value) || 1));
                    setNumResources(n);
                    setAllocation(allocation.map(row => {
                      if (row.length < n) return [...row, ...new Array(n - row.length).fill(0)];
                      return row.slice(0, n);
                    }));
                    if (available.length < n) setAvailable([...available, ...new Array(n - available.length).fill(0)]);
                    else setAvailable(available.slice(0, n));
                  }}
                  className="w-14 bg-slate-800 border border-white/10 rounded px-2 py-1 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th className="p-2 text-slate-500 text-xs uppercase">Process</th>
                    {resourceLabels.map(r => <th key={r} className="p-2 text-slate-500 text-xs uppercase">{r}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {deadlockedProcesses.map((p, i) => (
                    <tr key={p} className="border-t border-white/5">
                      <td className="p-2 font-mono text-blue-400 text-sm">{p}</td>
                      {resourceLabels.map((_, j) => (
                        <td key={j} className="p-1">
                          <input
                            type="number"
                            value={allocation[i]?.[j] ?? 0}
                            onChange={(e) => updateAllocation(i, j, e.target.value)}
                            className="w-16 bg-slate-800 border border-white/10 rounded px-2 py-1 text-white text-sm focus:outline-none focus:border-blue-500"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Available Resources */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Available Resources</h3>
            <div className="flex gap-4">
              {resourceLabels.map((r, i) => (
                <div key={r} className="flex flex-col gap-1">
                  <label className="text-xs text-slate-500 uppercase">{r}</label>
                  <input
                    type="number"
                    value={available[i] ?? 0}
                    onChange={(e) => {
                      const newAvail = [...available];
                      newAvail[i] = parseInt(e.target.value) || 0;
                      setAvailable(newAvail);
                    }}
                    className="w-20 bg-slate-800 border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Recovery Result */}
          {result && (
            <div className="bg-slate-900/50 border border-emerald-500/20 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-emerald-400 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                Recovery Log
              </h3>
              <div className="space-y-3">
                {result.recovery_steps.map((step: string, i: number) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center text-[10px] text-emerald-400 font-bold shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <p className="text-slate-300">{step}</p>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-white/5 flex items-center justify-between">
                <div className="text-xs text-slate-500">
                  Strategy: <span className="text-slate-300 font-mono">{result.strategy_used}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-xs text-emerald-400 font-bold uppercase">System Safe</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecoveryPage;
