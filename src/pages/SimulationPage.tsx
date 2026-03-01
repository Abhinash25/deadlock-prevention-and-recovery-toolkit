import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Activity, Cpu, Database, Terminal, ShieldAlert } from 'lucide-react';
import { cn } from '../lib/utils';
import { useSystem } from '../lib/SystemContext';

const SimulationPage = () => {
  const { system } = useSystem();
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(50);
  const [numProcesses, setNumProcesses] = useState(system.numProcesses);
  const [numResources, setNumResources] = useState(system.numResources);
  const [logs, setLogs] = useState<{ text: string; type: 'safe' | 'unsafe' | 'info' | 'denied' }[]>([]);
  const [stats, setStats] = useState({
    running: 0,
    blocked: 0,
    totalSteps: 0,
    status: 'idle' as 'idle' | 'safe' | 'unsafe',
  });
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Sync from context
  useEffect(() => {
    if (system.isConfigured) {
      setNumProcesses(system.numProcesses);
      setNumResources(system.numResources);
    }
  }, [system]);

  const runSingleSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numProcesses, numResources })
      });
      const data = await response.json();

      const newLogs = data.analysis_log.map((line: string) => ({
        text: line,
        type: line.includes('Denied') || line.includes('UNSAFE')
          ? 'denied'
          : line.includes('SAFE')
            ? 'safe'
            : line.includes('---')
              ? 'info'
              : 'info',
      }));

      setLogs(prev => [...newLogs, ...prev].slice(0, 100));
      setStats(prev => ({
        running: data.running_processes.length,
        blocked: data.blocked_processes.length,
        totalSteps: prev.totalSteps + 1,
        status: data.status,
      }));
    } catch (error) {
      console.error('Simulation error:', error);
    }
  };

  useEffect(() => {
    let interval: any;
    if (isRunning) {
      // Run immediately on start
      runSingleSimulation();
      interval = setInterval(runSingleSimulation, Math.max(500, (100 - speed) * 40));
    }
    return () => clearInterval(interval);
  }, [isRunning, speed, numProcesses, numResources]);

  // Scroll to bottom on new logs
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = 0;
    }
  }, [logs]);

  const handleReset = () => {
    setIsRunning(false);
    setLogs([]);
    setStats({ running: 0, blocked: 0, totalSteps: 0, status: 'idle' });
  };

  const handleRunOnce = async () => {
    await runSingleSimulation();
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Simulation Engine</h2>
          <p className="text-slate-400">Real-time deadlock scenario simulation using Banker's Algorithm</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRunOnce}
            disabled={isRunning}
            className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-900/20 disabled:opacity-50"
          >
            <Play className="w-5 h-5" />
            Run Once
          </button>
          <button
            onClick={() => setIsRunning(!isRunning)}
            className={cn(
              "px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg",
              isRunning
                ? "bg-amber-600 hover:bg-amber-500 shadow-amber-900/20"
                : "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/20"
            )}
          >
            {isRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            {isRunning ? 'Pause' : 'Auto-Run'}
          </button>
          <button
            onClick={handleReset}
            className="bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all border border-white/5"
          >
            <RotateCcw className="w-5 h-5" />
            Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {[
          { label: 'Running Processes', value: stats.running, icon: Cpu, color: 'text-blue-400', bg: 'bg-blue-500/10' },
          { label: 'Blocked Processes', value: stats.blocked, icon: Activity, color: 'text-red-400', bg: 'bg-red-500/10' },
          { label: 'Simulations Run', value: stats.totalSteps, icon: Database, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
          { label: 'System Health', value: stats.status === 'idle' ? 'Idle' : stats.status === 'safe' ? 'Safe' : 'Unsafe', icon: ShieldAlert, color: stats.status === 'unsafe' ? 'text-red-400' : stats.status === 'safe' ? 'text-emerald-400' : 'text-slate-400', bg: stats.status === 'unsafe' ? 'bg-red-500/10' : stats.status === 'safe' ? 'bg-emerald-500/10' : 'bg-slate-500/10' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={cn("p-3 rounded-xl", stat.bg)}>
                <stat.icon className={cn("w-6 h-6", stat.color)} />
              </div>
              <span className={cn("text-2xl font-bold", stat.color)}>{stat.value}</span>
            </div>
            <p className="text-sm text-slate-500 font-medium">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">Configuration</h3>
            <div className="space-y-5">
              <div>
                <label className="block text-sm text-slate-400 mb-2">Number of Processes</label>
                <input
                  type="number"
                  min={2}
                  max={10}
                  value={numProcesses}
                  onChange={(e) => setNumProcesses(Math.max(2, Math.min(10, parseInt(e.target.value) || 2)))}
                  disabled={isRunning}
                  className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-2">Number of Resources</label>
                <input
                  type="number"
                  min={1}
                  max={6}
                  value={numResources}
                  onChange={(e) => setNumResources(Math.max(1, Math.min(6, parseInt(e.target.value) || 1)))}
                  disabled={isRunning}
                  className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm text-slate-400">Auto-Run Speed</label>
                  <span className="text-sm text-blue-400 font-mono">{speed}%</span>
                </div>
                <input
                  type="range"
                  min={10}
                  max={90}
                  value={speed}
                  onChange={(e) => setSpeed(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>

              <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-xl">
                <p className="text-xs text-blue-400 font-bold uppercase mb-1">How it Works</p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Each simulation generates a random system with the specified processes and resources,
                  then simulates resource requests step-by-step using Banker's Algorithm to check safety.
                  Unsafe requests are automatically denied.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-slate-950 border border-white/10 rounded-2xl overflow-hidden flex flex-col h-[500px]">
            <div className="bg-slate-900 px-6 py-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-slate-500" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Simulation Log</h3>
                {isRunning && <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse ml-2" />}
              </div>
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500/50" />
                <div className="w-2 h-2 rounded-full bg-amber-500/50" />
                <div className="w-2 h-2 rounded-full bg-emerald-500/50" />
              </div>
            </div>
            <div ref={logContainerRef} className="flex-1 p-6 font-mono text-sm overflow-y-auto space-y-1">
              {logs.length === 0 && (
                <div className="h-full flex items-center justify-center text-slate-600 italic">
                  Click "Run Once" or "Auto-Run" to start simulation...
                </div>
              )}
              {logs.map((log, i) => (
                <div key={i} className={cn(
                  "border-l-2 pl-4 py-0.5 text-xs",
                  log.text.includes('Denied') || log.text.includes('UNSAFE')
                    ? "border-red-500 text-red-400 bg-red-500/5"
                    : log.text.includes('Granted') || log.text.includes('SAFE')
                      ? "border-emerald-800 text-emerald-400"
                      : log.text.includes('---')
                        ? "border-blue-500 text-blue-400 font-bold"
                        : "border-slate-800 text-slate-500"
                )}>
                  {log.text}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationPage;
