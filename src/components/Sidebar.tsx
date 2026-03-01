import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldCheck,
  Search,
  RotateCcw,
  PlayCircle,
  Settings
} from 'lucide-react';
import { cn } from '../lib/utils';

const Sidebar = () => {
  const navItems = [
    { name: 'System Setup', path: '/', icon: Settings },
    { name: 'Banker\'s Algorithm', path: '/bankers', icon: ShieldCheck },
    { name: 'Deadlock Detection', path: '/detection', icon: Search },
    { name: 'Recovery', path: '/recovery', icon: RotateCcw },
    { name: 'Simulation', path: '/simulation', icon: PlayCircle },
  ];

  return (
    <div className="w-64 bg-slate-950 border-r border-white/10 flex flex-col h-screen sticky top-0">
      <div className="p-6 border-b border-white/10">
        <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent leading-tight">
          Deadlock Prevention & Recovery Toolkit
        </h1>
        <p className="text-xs text-slate-500 mt-1">OS Project v1.0</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group",
              isActive
                ? "bg-blue-600/10 text-blue-400 border border-blue-500/20"
                : "text-slate-400 hover:bg-white/5 hover:text-white"
            )}
          >
            <item.icon className={cn(
              "w-5 h-5",
              "group-hover:scale-110 transition-transform"
            )} />
            <span className="font-medium">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className="bg-slate-900 rounded-lg p-3 border border-white/5">
          <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-1">System Status</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-emerald-400 font-medium">Engine Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
