import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { ProcessData, ResourceData } from '../../lib/ragTypes';
import { Box, Layers, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

export const ProcessNode = memo(({ data, selected }: NodeProps<ProcessData>) => {
    return (
        <div
            className={cn(
                "relative min-w-[150px] px-4 py-3 rounded-xl border transition-all duration-200 group shadow-sm",
                "bg-white",
                data.isDeadlocked
                    ? "border-red-300 ring-2 ring-red-100 shadow-red-100"
                    : "border-stone-200 shadow-stone-100",
                selected && !data.isDeadlocked
                    ? "ring-2 ring-blue-100 border-blue-300"
                    : "",
                "hover:shadow-md hover:border-stone-300"
            )}
        >
            <div className="flex items-center gap-2.5 mb-1.5">
                <div className={cn(
                    "p-1.5 rounded-lg",
                    data.isDeadlocked
                        ? "bg-red-50 text-red-500"
                        : "bg-blue-50 text-blue-500"
                )}>
                    {data.isDeadlocked ? <AlertCircle size={14} /> : <Box size={14} />}
                </div>
                <span className="text-sm font-semibold text-stone-800">{data.label}</span>
            </div>
            <div className="text-xs text-stone-500 font-mono">
                PID: {data.pid}
            </div>

            <div className="mt-2 pt-2 border-t border-stone-100 text-[10px] text-stone-400 uppercase tracking-wider flex justify-between">
                <span>Process</span>
                {data.isDeadlocked && <span className="text-red-500 font-bold animate-pulse">STUCK</span>}
            </div>

            <Handle
                type="target"
                position={Position.Top}
                className="!bg-blue-500 !w-2.5 !h-2.5 !border-2 !border-white"
            />
            <Handle
                type="source"
                position={Position.Bottom}
                className="!bg-blue-500 !w-2.5 !h-2.5 !border-2 !border-white"
            />
        </div>
    );
});

export const ResourceNode = memo(({ data, selected }: NodeProps<ResourceData>) => {
    return (
        <div
            className={cn(
                "relative min-w-[150px] px-4 py-3 rounded-xl border transition-all duration-200 shadow-sm",
                "bg-white",
                data.isDeadlocked
                    ? "border-red-300 ring-2 ring-red-100 shadow-red-100"
                    : "border-stone-200 shadow-stone-100",
                selected && !data.isDeadlocked
                    ? "ring-2 ring-emerald-100 border-emerald-300"
                    : "",
                "hover:shadow-md hover:border-stone-300"
            )}
        >
            <div className="flex items-center gap-2.5 mb-1.5">
                <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-500">
                    <Layers size={14} />
                </div>
                <span className="text-sm font-semibold text-stone-800">{data.label}</span>
            </div>

            <div className="flex items-center gap-2 mt-1">
                <span className="text-xs px-2 py-0.5 rounded-md bg-stone-50 text-emerald-600 border border-stone-200 font-mono">
                    {data.instances} {data.instances === 1 ? 'unit' : 'units'}
                </span>
            </div>

            <div className="mt-2 pt-2 border-t border-stone-100 text-[10px] text-stone-400 uppercase tracking-wider flex justify-between">
                <span>Resource</span>
            </div>

            <Handle
                type="target"
                position={Position.Top}
                className="!bg-emerald-500 !w-2.5 !h-2.5 !border-2 !border-white"
            />
            <Handle
                type="source"
                position={Position.Bottom}
                className="!bg-emerald-500 !w-2.5 !h-2.5 !border-2 !border-white"
            />
        </div>
    );
});
