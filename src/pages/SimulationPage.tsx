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
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-stone-800">Simulation Engine</h2>
          <p className="text-stone-500 mt-1">Real-time deadlock scenario simulation using Banker's Algorithm</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRunOnce}
            disabled={isRunning}
            className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2.5 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm disabled:opacity-50 text-sm"
          >
            <Play className="w-4 h-4" />
            Run Once
          </button>
          <button
            onClick={() => setIsRunning(!isRunning)}
            className={cn(
              "px-5 py-2.5 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm text-white",
              isRunning
                ? "bg-amber-500 hover:bg-amber-600"
                : "bg-emerald-500 hover:bg-emerald-600"
            )}
          >
            {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isRunning ? 'Pause' : 'Auto-Run'}
          </button>
          <button
            onClick={handleReset}
            className="bg-stone-100 hover:bg-stone-200 text-stone-700 px-4 py-2.5 rounded-lg font-semibold flex items-center gap-2 transition-colors border border-stone-200 text-sm"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {[
          { label: 'Running Processes', value: stats.running, icon: Cpu, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
          { label: 'Blocked Processes', value: stats.blocked, icon: Activity, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
          { label: 'Simulations Run', value: stats.totalSteps, icon: Database, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200' },
          { label: 'System Health', value: stats.status === 'idle' ? 'Idle' : stats.status === 'safe' ? 'Safe' : 'Unsafe', icon: ShieldAlert, color: stats.status === 'unsafe' ? 'text-red-600' : stats.status === 'safe' ? 'text-emerald-600' : 'text-stone-500', bg: stats.status === 'unsafe' ? 'bg-red-50' : stats.status === 'safe' ? 'bg-emerald-50' : 'bg-stone-50', border: stats.status === 'unsafe' ? 'border-red-200' : stats.status === 'safe' ? 'border-emerald-200' : 'border-stone-200' },
        ].map((stat, i) => (
          <div key={i} className={cn("bg-white border rounded-xl p-5 shadow-sm", stat.border)}>
            <div className="flex items-center justify-between mb-3">
              <div className={cn("p-2.5 rounded-lg", stat.bg)}>
                <stat.icon className={cn("w-5 h-5", stat.color)} />
              </div>
              <span className={cn("text-2xl font-bold", stat.color)}>{stat.value}</span>
            </div>
            <p className="text-sm text-stone-500 font-medium">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-base font-semibold text-stone-800 mb-4">Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-stone-500 mb-1.5">Number of Processes</label>
                <input
                  type="number"
                  min={2}
                  max={10}
                  value={numProcesses}
                  onChange={(e) => setNumProcesses(Math.max(2, Math.min(10, parseInt(e.target.value) || 2)))}
                  disabled={isRunning}
                  className="w-full bg-stone-50 border border-stone-200 rounded-lg px-4 py-2.5 text-stone-800 focus:outline-none focus:border-orange-400 disabled:opacity-50"
                />
              </div>
              <div>
                <label className="block text-sm text-stone-500 mb-1.5">Number of Resources</label>
                <input
                  type="number"
                  min={1}
                  max={6}
                  value={numResources}
                  onChange={(e) => setNumResources(Math.max(1, Math.min(6, parseInt(e.target.value) || 1)))}
                  disabled={isRunning}
                  className="w-full bg-stone-50 border border-stone-200 rounded-lg px-4 py-2.5 text-stone-800 focus:outline-none focus:border-orange-400 disabled:opacity-50"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1.5">
                  <label className="text-sm text-stone-500">Auto-Run Speed</label>
                  <span className="text-sm text-orange-600 font-mono">{speed}%</span>
                </div>
                <input
                  type="range"
                  min={10}
                  max={90}
                  value={speed}
                  onChange={(e) => setSpeed(parseInt(e.target.value))}
                  className="w-full h-2 bg-stone-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
                />
              </div>

              <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="text-xs text-orange-700 font-bold uppercase mb-1">How it Works</p>
                <p className="text-xs text-stone-500 leading-relaxed">
                  Each simulation generates a random system with the specified processes and resources,
                  then simulates resource requests step-by-step using Banker's Algorithm to check safety.
                  Unsafe requests are automatically denied.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          {/* Terminal-style log — kept dark for Notion code-block feel */}
          <div className="bg-stone-900 border border-stone-700 rounded-xl overflow-hidden flex flex-col h-[500px]">
            <div className="bg-stone-800 px-5 py-3 border-b border-stone-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-stone-400" />
                <h3 className="text-sm font-bold text-stone-200 uppercase tracking-wider">Simulation Log</h3>
                {isRunning && <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse ml-2" />}
              </div>
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/60" />
                <div className="w-3 h-3 rounded-full bg-amber-500/60" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/60" />
              </div>
            </div>
            <div ref={logContainerRef} className="flex-1 p-5 font-mono text-sm overflow-y-auto space-y-1">
              {logs.length === 0 && (
                <div className="h-full flex items-center justify-center text-stone-600 italic">
                  Click "Run Once" or "Auto-Run" to start simulation...
                </div>
              )}
              {logs.map((log, i) => (
                <div key={i} className={cn(
                  "border-l-2 pl-4 py-0.5 text-xs",
                  log.text.includes('Denied') || log.text.includes('UNSAFE')
                    ? "border-red-500 text-red-400 bg-red-500/5"
                    : log.text.includes('Granted') || log.text.includes('SAFE')
                      ? "border-emerald-600 text-emerald-400"
                      : log.text.includes('---')
                        ? "border-blue-500 text-blue-400 font-bold"
                        : "border-stone-700 text-stone-500"
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
