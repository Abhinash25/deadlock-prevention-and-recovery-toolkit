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
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-stone-800">Deadlock Recovery</h2>
        <p className="text-stone-500 mt-1">Strategies to break cycles and restore system safety</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-4">Select Strategy</h3>
            <div className="space-y-2">
              {[
                { id: 'terminate-all', name: 'Terminate All', icon: Trash2, desc: 'Stop all processes in the deadlock cycle simultaneously.' },
                { id: 'terminate-one-by-one', name: 'One-by-One', icon: Zap, desc: 'Terminate processes sequentially until cycle is broken.' },
                { id: 'preemption', name: 'Resource Preemption', icon: RotateCcw, desc: 'Take resources away from processes and give to others.' },
              ].map((s) => (
                <button
                  key={s.id}
                  onClick={() => setStrategy(s.id as any)}
                  className={cn(
                    "w-full text-left p-3.5 rounded-lg border transition-all group",
                    strategy === s.id
                      ? "bg-orange-50 border-orange-200 text-stone-800"
                      : "bg-stone-50 border-stone-200 text-stone-600 hover:border-stone-300 hover:bg-stone-100"
                  )}
                >
                  <div className="flex items-center gap-3 mb-1">
                    <s.icon className={cn(
                      "w-4 h-4",
                      strategy === s.id ? "text-orange-500" : "text-stone-400"
                    )} />
                    <span className="font-semibold text-sm">{s.name}</span>
                  </div>
                  <p className="text-xs text-stone-500">
                    {s.desc}
                  </p>
                </button>
              ))}
            </div>

            <button
              onClick={handleRecover}
              disabled={loading || deadlockedProcesses.length === 0}
              className="w-full mt-6 bg-emerald-500 hover:bg-emerald-600 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors shadow-sm disabled:opacity-50"
            >
              <RotateCcw className="w-4 h-4" />
              {loading ? 'Executing...' : 'Execute Recovery'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {/* Deadlocked Processes Configuration */}
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-3">Deadlocked Processes</h3>

            {/* Add process */}
            <div className="flex gap-2 mb-4">
              <input
                placeholder="Process ID (e.g. P3)"
                value={newProcessId}
                onChange={(e) => setNewProcessId(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addProcess()}
                className="flex-1 bg-stone-50 border border-stone-200 rounded-lg px-3 py-2 text-sm text-stone-800 focus:outline-none focus:border-orange-400"
              />
              <button onClick={addProcess} className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-semibold text-sm flex items-center gap-1 transition-colors">
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>

            {/* Process Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {deadlockedProcesses.map((p, idx) => (
                <div key={p} className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-red-100 rounded-lg flex items-center justify-center text-red-600 font-bold text-xs">
                      {p}
                    </div>
                    <div>
                      <span className="text-stone-700 font-medium text-sm">{p}</span>
                      <div className="text-[9px] text-red-500 uppercase font-bold">Blocked</div>
                    </div>
                  </div>
                  <button onClick={() => removeProcess(idx)} className="text-stone-400 hover:text-red-500 transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Allocation Matrix */}
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-semibold text-stone-800">Allocation Matrix</h3>
              <div className="flex items-center gap-2">
                <label className="text-xs text-stone-500">Resources:</label>
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
                  className="w-14 bg-stone-50 border border-stone-200 rounded px-2 py-1 text-stone-800 text-sm focus:outline-none focus:border-orange-400"
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th className="p-2 text-stone-400 text-xs uppercase">Process</th>
                    {resourceLabels.map(r => <th key={r} className="p-2 text-stone-400 text-xs uppercase">{r}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {deadlockedProcesses.map((p, i) => (
                    <tr key={p} className="border-t border-stone-100">
                      <td className="p-2 font-mono text-orange-600 text-sm">{p}</td>
                      {resourceLabels.map((_, j) => (
                        <td key={j} className="p-1">
                          <input
                            type="number"
                            value={allocation[i]?.[j] ?? 0}
                            onChange={(e) => updateAllocation(i, j, e.target.value)}
                            className="w-16 bg-stone-50 border border-stone-200 rounded px-2 py-1 text-stone-800 text-sm focus:outline-none focus:border-orange-400"
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
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-3">Available Resources</h3>
            <div className="flex gap-4">
              {resourceLabels.map((r, i) => (
                <div key={r} className="flex flex-col gap-1">
                  <label className="text-xs text-stone-400 uppercase">{r}</label>
                  <input
                    type="number"
                    value={available[i] ?? 0}
                    onChange={(e) => {
                      const newAvail = [...available];
                      newAvail[i] = parseInt(e.target.value) || 0;
                      setAvailable(newAvail);
                    }}
                    className="w-20 bg-stone-50 border border-stone-200 rounded px-3 py-2 text-stone-800 focus:outline-none focus:border-amber-400"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Recovery Result */}
          {result && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
              <h3 className="text-base font-semibold text-emerald-700 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                Recovery Log
              </h3>
              <div className="space-y-2.5">
                {result.recovery_steps.map((step: string, i: number) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-[10px] text-emerald-700 font-bold shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <p className="text-stone-700">{step}</p>
                  </div>
                ))}
              </div>
              <div className="mt-5 pt-5 border-t border-emerald-200 flex items-center justify-between">
                <div className="text-xs text-stone-500">
                  Strategy: <span className="text-stone-700 font-mono">{result.strategy_used}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-xs text-emerald-700 font-bold uppercase">System Safe</span>
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
