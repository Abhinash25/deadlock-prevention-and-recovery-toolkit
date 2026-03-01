import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, Cpu, Database, Sparkles, ArrowRight, RotateCcw, Zap } from 'lucide-react';
import { cn } from '../lib/utils';
import { useSystem } from '../lib/SystemContext';

const SetupPage = () => {
  const navigate = useNavigate();
  const { system, generateSystem, resetSystem } = useSystem();
  const [numProcesses, setNumProcesses] = useState(system.numProcesses);
  const [numResources, setNumResources] = useState(system.numResources);

  const handleGenerate = () => {
    generateSystem(numProcesses, numResources);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-stone-800">System Setup</h2>
        <p className="text-stone-500 mt-1">Configure the system parameters and generate resource allocation data</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-stone-200 rounded-xl p-6 space-y-4 shadow-sm">
          <h3 className="text-base font-semibold text-stone-800 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-orange-500" />
            Process Configuration
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-stone-500 mb-1.5">Number of Processes</label>
              <input
                type="number"
                min={2}
                max={10}
                value={numProcesses}
                onChange={(e) => setNumProcesses(Math.max(2, Math.min(10, parseInt(e.target.value) || 2)))}
                className="w-full bg-stone-50 border border-stone-200 rounded-lg px-4 py-2.5 text-stone-800 focus:outline-none focus:border-orange-400 focus:ring-1 focus:ring-orange-100 transition-colors"
              />
            </div>
            <p className="text-xs text-stone-400">Processes will be named P0, P1, P2…</p>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-xl p-6 space-y-4 shadow-sm">
          <h3 className="text-base font-semibold text-stone-800 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-500" />
            Resource Configuration
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-stone-500 mb-1.5">Number of Resource Types</label>
              <input
                type="number"
                min={1}
                max={8}
                value={numResources}
                onChange={(e) => setNumResources(Math.max(1, Math.min(8, parseInt(e.target.value) || 1)))}
                className="w-full bg-stone-50 border border-stone-200 rounded-lg px-4 py-2.5 text-stone-800 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition-colors"
              />
            </div>
            <p className="text-xs text-stone-400">Resources will be named A, B, C…</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleGenerate}
          className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2.5 transition-colors shadow-sm text-base"
        >
          <Sparkles className="w-5 h-5" />
          Generate System
        </button>
        <button
          onClick={resetSystem}
          className="bg-stone-100 hover:bg-stone-200 text-stone-700 px-5 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors border border-stone-200"
        >
          <RotateCcw className="w-4 h-4" />
          Reset to Default
        </button>
      </div>

      {/* Generated System Preview */}
      {system.isConfigured && (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <h3 className="text-lg font-bold text-emerald-700">System Generated Successfully</h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Allocation Matrix */}
            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
              <h4 className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-3">Allocation Matrix</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      <th className="p-1 text-stone-400 text-xs"></th>
                      {system.resources.map(r => <th key={r} className="p-1 text-stone-400 text-xs">{r}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {system.processes.map((p, i) => (
                      <tr key={p} className="border-t border-stone-100">
                        <td className="p-1 font-mono text-orange-600 text-xs">{p}</td>
                        {system.resources.map((_, j) => (
                          <td key={j} className="p-1 text-center text-stone-700 font-mono text-xs">{system.allocation[i][j]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Max Matrix */}
            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
              <h4 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-3">Max Matrix</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      <th className="p-1 text-stone-400 text-xs"></th>
                      {system.resources.map(r => <th key={r} className="p-1 text-stone-400 text-xs">{r}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {system.processes.map((p, i) => (
                      <tr key={p} className="border-t border-stone-100">
                        <td className="p-1 font-mono text-blue-600 text-xs">{p}</td>
                        {system.resources.map((_, j) => (
                          <td key={j} className="p-1 text-center text-stone-700 font-mono text-xs">{system.max[i][j]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Available Vector */}
            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
              <h4 className="text-xs font-bold text-amber-600 uppercase tracking-wider mb-3">Available Resources</h4>
              <div className="flex flex-wrap gap-3 mt-2">
                {system.resources.map((r, i) => (
                  <div key={r} className="bg-stone-50 border border-stone-200 rounded-lg px-4 py-3 text-center">
                    <div className="text-[10px] text-stone-400 uppercase mb-1">{r}</div>
                    <div className="text-xl font-bold text-stone-800 font-mono">{system.available[i]}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Navigation */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              onClick={() => navigate('/bankers')}
              className="bg-orange-50 border border-orange-200 hover:border-orange-300 rounded-xl p-5 text-left transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-stone-800 font-bold mb-1">Banker's Algorithm</h4>
                  <p className="text-xs text-stone-500">Run safety check with this data</p>
                </div>
                <ArrowRight className="w-5 h-5 text-orange-500 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
            <button
              onClick={() => navigate('/detection')}
              className="bg-blue-50 border border-blue-200 hover:border-blue-300 rounded-xl p-5 text-left transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-stone-800 font-bold mb-1">Deadlock Detection</h4>
                  <p className="text-xs text-stone-500">Detect cycles in RAG</p>
                </div>
                <ArrowRight className="w-5 h-5 text-blue-500 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
            <button
              onClick={() => navigate('/simulation')}
              className="bg-amber-50 border border-amber-200 hover:border-amber-300 rounded-xl p-5 text-left transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-stone-800 font-bold mb-1">Simulation</h4>
                  <p className="text-xs text-stone-500">Simulate deadlock scenarios</p>
                </div>
                <ArrowRight className="w-5 h-5 text-amber-500 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          </div>
        </div>
      )}

    </div>
  );
};

export default SetupPage;
