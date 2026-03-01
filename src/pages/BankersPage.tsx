import React, { useState, useEffect } from 'react';
import { Play, ShieldCheck } from 'lucide-react';
import { cn } from '../lib/utils';
import { useSystem } from '../lib/SystemContext';

const BankersPage = () => {
  const { system } = useSystem();
  const [processes, setProcesses] = useState(system.processes);
  const [resources, setResources] = useState(system.resources);
  const [allocation, setAllocation] = useState(system.allocation);
  const [max, setMax] = useState(system.max);
  const [available, setAvailable] = useState(system.available);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Sync from shared context when it changes
  useEffect(() => {
    setProcesses(system.processes);
    setResources(system.resources);
    setAllocation(system.allocation);
    setMax(system.max);
    setAvailable(system.available);
    setResult(null);
  }, [system]);

  const handleRun = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/bankers/safety-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ processes, resources, allocation, max, available })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updateMatrix = (matrix: number[][], setMatrix: any, r: number, c: number, val: string) => {
    const newMatrix = matrix.map((row, i) => i === r ? [...row] : row);
    newMatrix[r][c] = parseInt(val) || 0;
    setMatrix(newMatrix);
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Banker's Algorithm</h2>
          <p className="text-slate-400">Deadlock prevention through safety state analysis</p>
        </div>
        <button
          onClick={handleRun}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-900/20 disabled:opacity-50"
        >
          <Play className="w-5 h-5" />
          {loading ? 'Analyzing...' : 'Run Safety Check'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              Allocation Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th className="p-2 text-slate-500 text-xs uppercase">Process</th>
                    {resources.map(r => <th key={r} className="p-2 text-slate-500 text-xs uppercase">{r}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {processes.map((p, i) => (
                    <tr key={p} className="border-t border-white/5">
                      <td className="p-2 font-mono text-blue-400">{p}</td>
                      {resources.map((_, j) => (
                        <td key={j} className="p-1">
                          <input
                            type="number"
                            value={allocation[i]?.[j] ?? 0}
                            onChange={(e) => updateMatrix(allocation, setAllocation, i, j, e.target.value)}
                            className="w-16 bg-slate-800 border border-white/10 rounded px-2 py-1 text-white focus:outline-none focus:border-blue-500"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Max Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th className="p-2 text-slate-500 text-xs uppercase">Process</th>
                    {resources.map(r => <th key={r} className="p-2 text-slate-500 text-xs uppercase">{r}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {processes.map((p, i) => (
                    <tr key={p} className="border-t border-white/5">
                      <td className="p-2 font-mono text-emerald-400">{p}</td>
                      {resources.map((_, j) => (
                        <td key={j} className="p-1">
                          <input
                            type="number"
                            value={max[i]?.[j] ?? 0}
                            onChange={(e) => updateMatrix(max, setMax, i, j, e.target.value)}
                            className="w-16 bg-slate-800 border border-white/10 rounded px-2 py-1 text-white focus:outline-none focus:border-emerald-500"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Available Resources
            </h3>
            <div className="flex gap-4">
              {resources.map((r, i) => (
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
        </div>

        <div className="space-y-6">
          {result ? (
            <>
              <div className={cn(
                "rounded-2xl p-6 border transition-all",
                result.safe ? "bg-emerald-500/10 border-emerald-500/20" : "bg-red-500/10 border-red-500/20"
              )}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className={cn(
                    "text-xl font-bold",
                    result.safe ? "text-emerald-400" : "text-red-400"
                  )}>
                    {result.safe ? 'System is SAFE ✓' : 'System is UNSAFE ✗'}
                  </h3>
                  {result.safe && (
                    <div className="bg-emerald-500 text-white text-[10px] font-bold px-2 py-1 rounded uppercase">
                      Safe Sequence Found
                    </div>
                  )}
                </div>

                {result.safe && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {result.safe_sequence.map((p: string, i: number) => (
                      <React.Fragment key={p}>
                        <div className="bg-slate-800 border border-white/10 rounded-lg px-4 py-2 text-white font-mono">
                          {p}
                        </div>
                        {i < result.safe_sequence.length - 1 && (
                          <div className="flex items-center text-slate-600">→</div>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                )}

                <div className="bg-slate-950/50 rounded-xl p-4 font-mono text-sm space-y-2 max-h-[300px] overflow-y-auto">
                  {result.log.map((line: string, i: number) => (
                    <div key={i} className="text-slate-400">
                      <span className="text-slate-600 mr-2">[{i + 1}]</span>
                      {line}
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Need Matrix (Calculated)</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr>
                        <th className="p-2 text-slate-500 text-xs uppercase">Process</th>
                        {resources.map(r => <th key={r} className="p-2 text-slate-500 text-xs uppercase">{r}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {processes.map((p, i) => (
                        <tr key={p} className="border-t border-white/5">
                          <td className="p-2 font-mono text-slate-400">{p}</td>
                          {resources.map((_, j) => (
                            <td key={j} className="p-2 text-white font-mono">
                              {result.need_matrix[i]?.[j] ?? 0}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-slate-900/20 border border-dashed border-white/10 rounded-2xl">
              <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
                <ShieldCheck className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="text-lg font-medium text-slate-400">Ready for Analysis</h3>
              <p className="text-sm text-slate-500 max-w-xs mt-2">
                Configure the matrices and run the safety algorithm to see the results here.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BankersPage;
