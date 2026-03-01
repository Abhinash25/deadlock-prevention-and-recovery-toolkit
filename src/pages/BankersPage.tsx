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
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-stone-800">Banker's Algorithm</h2>
          <p className="text-stone-500 mt-1">Deadlock prevention through safety state analysis</p>
        </div>
        <button
          onClick={handleRun}
          disabled={loading}
          className="bg-orange-500 hover:bg-orange-600 text-white px-5 py-2.5 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm disabled:opacity-50"
        >
          <Play className="w-4 h-4" />
          {loading ? 'Analyzing...' : 'Run Safety Check'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-orange-500" />
              Allocation Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th className="p-2 text-stone-400 text-xs uppercase">Process</th>
                    {resources.map(r => <th key={r} className="p-2 text-stone-400 text-xs uppercase">{r}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {processes.map((p, i) => (
                    <tr key={p} className="border-t border-stone-100">
                      <td className="p-2 font-mono text-orange-600">{p}</td>
                      {resources.map((_, j) => (
                        <td key={j} className="p-1">
                          <input
                            type="number"
                            value={allocation[i]?.[j] ?? 0}
                            onChange={(e) => updateMatrix(allocation, setAllocation, i, j, e.target.value)}
                            className="w-16 bg-stone-50 border border-stone-200 rounded px-2 py-1 text-stone-800 focus:outline-none focus:border-orange-400"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              Max Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th className="p-2 text-stone-400 text-xs uppercase">Process</th>
                    {resources.map(r => <th key={r} className="p-2 text-stone-400 text-xs uppercase">{r}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {processes.map((p, i) => (
                    <tr key={p} className="border-t border-stone-100">
                      <td className="p-2 font-mono text-blue-600">{p}</td>
                      {resources.map((_, j) => (
                        <td key={j} className="p-1">
                          <input
                            type="number"
                            value={max[i]?.[j] ?? 0}
                            onChange={(e) => updateMatrix(max, setMax, i, j, e.target.value)}
                            className="w-16 bg-stone-50 border border-stone-200 rounded px-2 py-1 text-stone-800 focus:outline-none focus:border-blue-400"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Available Resources
            </h3>
            <div className="flex gap-4">
              {resources.map((r, i) => (
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
        </div>

        <div className="space-y-4">
          {result ? (
            <>
              <div className={cn(
                "rounded-xl p-5 border transition-all",
                result.safe ? "bg-emerald-50 border-emerald-200" : "bg-red-50 border-red-200"
              )}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className={cn(
                    "text-lg font-bold",
                    result.safe ? "text-emerald-700" : "text-red-700"
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
                        <div className="bg-white border border-stone-200 rounded-lg px-4 py-2 text-stone-800 font-mono shadow-sm">
                          {p}
                        </div>
                        {i < result.safe_sequence.length - 1 && (
                          <div className="flex items-center text-stone-400">→</div>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                )}

                <div className="bg-stone-800 rounded-lg p-4 font-mono text-sm space-y-2 max-h-[300px] overflow-y-auto">
                  {result.log.map((line: string, i: number) => (
                    <div key={i} className="text-stone-400">
                      <span className="text-stone-600 mr-2">[{i + 1}]</span>
                      {line}
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
                <h3 className="text-base font-semibold text-stone-800 mb-4">Need Matrix (Calculated)</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr>
                        <th className="p-2 text-stone-400 text-xs uppercase">Process</th>
                        {resources.map(r => <th key={r} className="p-2 text-stone-400 text-xs uppercase">{r}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {processes.map((p, i) => (
                        <tr key={p} className="border-t border-stone-100">
                          <td className="p-2 font-mono text-stone-500">{p}</td>
                          {resources.map((_, j) => (
                            <td key={j} className="p-2 text-stone-700 font-mono">
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
            <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-stone-50 border border-dashed border-stone-300 rounded-xl">
              <div className="w-14 h-14 bg-stone-100 rounded-full flex items-center justify-center mb-4">
                <ShieldCheck className="w-7 h-7 text-stone-400" />
              </div>
              <h3 className="text-base font-medium text-stone-500">Ready for Analysis</h3>
              <p className="text-sm text-stone-400 max-w-xs mt-2">
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
