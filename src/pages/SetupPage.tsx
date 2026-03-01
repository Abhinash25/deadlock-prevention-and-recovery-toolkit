import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, Cpu, Database, Info, Sparkles, ArrowRight, RotateCcw, Zap } from 'lucide-react';
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
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white">System Setup</h2>
        <p className="text-slate-400">Configure the system parameters and generate resource allocation data</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6 space-y-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            Process Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-500 mb-2">Number of Processes</label>
              <input
                type="number"
                min={2}
                max={10}
                value={numProcesses}
                onChange={(e) => setNumProcesses(Math.max(2, Math.min(10, parseInt(e.target.value) || 2)))}
                className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <p className="text-xs text-slate-600">Processes will be named P0, P1, P2…</p>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6 space-y-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-emerald-400" />
            Resource Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-500 mb-2">Number of Resource Types</label>
              <input
                type="number"
                min={1}
                max={8}
                value={numResources}
                onChange={(e) => setNumResources(Math.max(1, Math.min(8, parseInt(e.target.value) || 1)))}
                className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <p className="text-xs text-slate-600">Resources will be named A, B, C…</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={handleGenerate}
          className="bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white px-8 py-4 rounded-xl font-bold flex items-center gap-3 transition-all shadow-lg shadow-blue-900/30 text-lg"
        >
          <Sparkles className="w-6 h-6" />
          Generate System
        </button>
        <button
          onClick={resetSystem}
          className="bg-slate-800 hover:bg-slate-700 text-white px-6 py-4 rounded-xl font-bold flex items-center gap-2 transition-all border border-white/5"
        >
          <RotateCcw className="w-5 h-5" />
          Reset to Default
        </button>
      </div>

      {/* Generated System Preview */}
      {system.isConfigured && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <h3 className="text-xl font-bold text-emerald-400">System Generated Successfully</h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Allocation Matrix */}
            <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-5">
              <h4 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-3">Allocation Matrix</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      <th className="p-1 text-slate-600 text-xs"></th>
                      {system.resources.map(r => <th key={r} className="p-1 text-slate-500 text-xs">{r}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {system.processes.map((p, i) => (
                      <tr key={p} className="border-t border-white/5">
                        <td className="p-1 font-mono text-blue-400 text-xs">{p}</td>
                        {system.resources.map((_, j) => (
                          <td key={j} className="p-1 text-center text-white font-mono text-xs">{system.allocation[i][j]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Max Matrix */}
            <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-5">
              <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-3">Max Matrix</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      <th className="p-1 text-slate-600 text-xs"></th>
                      {system.resources.map(r => <th key={r} className="p-1 text-slate-500 text-xs">{r}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {system.processes.map((p, i) => (
                      <tr key={p} className="border-t border-white/5">
                        <td className="p-1 font-mono text-emerald-400 text-xs">{p}</td>
                        {system.resources.map((_, j) => (
                          <td key={j} className="p-1 text-center text-white font-mono text-xs">{system.max[i][j]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Available Vector */}
            <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-5">
              <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider mb-3">Available Resources</h4>
              <div className="flex flex-wrap gap-3 mt-2">
                {system.resources.map((r, i) => (
                  <div key={r} className="bg-slate-800 border border-white/5 rounded-lg px-4 py-3 text-center">
                    <div className="text-[10px] text-slate-500 uppercase mb-1">{r}</div>
                    <div className="text-xl font-bold text-white font-mono">{system.available[i]}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Navigation */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/bankers')}
              className="bg-blue-600/10 border border-blue-500/20 hover:border-blue-500/50 rounded-xl p-5 text-left transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white font-bold mb-1">Banker's Algorithm</h4>
                  <p className="text-xs text-slate-500">Run safety check with this data</p>
                </div>
                <ArrowRight className="w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
            <button
              onClick={() => navigate('/detection')}
              className="bg-emerald-600/10 border border-emerald-500/20 hover:border-emerald-500/50 rounded-xl p-5 text-left transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white font-bold mb-1">Deadlock Detection</h4>
                  <p className="text-xs text-slate-500">Detect cycles in RAG</p>
                </div>
                <ArrowRight className="w-5 h-5 text-emerald-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
            <button
              onClick={() => navigate('/simulation')}
              className="bg-amber-600/10 border border-amber-500/20 hover:border-amber-500/50 rounded-xl p-5 text-left transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white font-bold mb-1">Simulation</h4>
                  <p className="text-xs text-slate-500">Simulate deadlock scenarios</p>
                </div>
                <ArrowRight className="w-5 h-5 text-amber-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          </div>
        </div>
      )}

      {/* Info Banner */}
      <div className="bg-blue-600/5 border border-blue-500/20 rounded-2xl p-8 flex gap-6">
        <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center shrink-0">
          <Info className="w-6 h-6 text-blue-400" />
        </div>
        <div className="space-y-2">
          <h4 className="text-white font-bold">About the Deadlock Toolkit</h4>
          <p className="text-slate-400 text-sm leading-relaxed">
            This toolkit is designed for academic demonstration of Operating System concepts.
            It implements the Banker's Algorithm for deadlock prevention, Resource Allocation Graphs
            for detection, and various termination/preemption strategies for recovery.
            Use the Setup page to generate system configurations, then explore each module.
          </p>
          <div className="pt-4 flex gap-4">
            <div className="text-[10px] bg-slate-800 text-slate-500 px-2 py-1 rounded font-bold uppercase">React 19</div>
            <div className="text-[10px] bg-slate-800 text-slate-500 px-2 py-1 rounded font-bold uppercase">D3.js</div>
            <div className="text-[10px] bg-slate-800 text-slate-500 px-2 py-1 rounded font-bold uppercase">Express</div>
            <div className="text-[10px] bg-slate-800 text-slate-500 px-2 py-1 rounded font-bold uppercase">Tailwind CSS</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SetupPage;
