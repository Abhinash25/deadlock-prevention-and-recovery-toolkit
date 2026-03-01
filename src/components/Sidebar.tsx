import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldCheck,
  Search,
  RotateCcw,
  PlayCircle,
  Settings,
  GitBranchPlus
} from 'lucide-react';
import { cn } from '../lib/utils';

const Sidebar = () => {
  const navItems = [
    { name: 'System Setup', path: '/', icon: Settings },
    { name: 'Banker\'s Algorithm', path: '/bankers', icon: ShieldCheck },
    { name: 'Deadlock Detection', path: '/detection', icon: Search },
    { name: 'Recovery', path: '/recovery', icon: RotateCcw },
    { name: 'Simulation', path: '/simulation', icon: PlayCircle },
    { name: 'RAG Visualizer', path: '/rag-visualizer', icon: GitBranchPlus },
  ];

  return (
    <div className="w-64 bg-stone-50 border-r border-stone-200 flex flex-col h-screen sticky top-0">
      <div className="p-6 border-b border-stone-200">
        <h1 className="text-lg font-bold text-stone-800 leading-tight">
          Deadlock Prevention & Recovery Toolkit
        </h1>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 group text-sm",
              isActive
                ? "bg-orange-50 text-orange-700 font-semibold"
                : "text-stone-500 hover:bg-stone-100 hover:text-stone-800"
            )}
          >
            <item.icon className={cn(
              "w-[18px] h-[18px]",
              "group-hover:scale-105 transition-transform"
            )} />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-stone-200">
        <div className="bg-white rounded-lg p-3 border border-stone-200">
          <p className="text-[10px] uppercase tracking-wider text-stone-400 font-bold mb-1">System Status</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-emerald-600 font-medium">Engine Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
