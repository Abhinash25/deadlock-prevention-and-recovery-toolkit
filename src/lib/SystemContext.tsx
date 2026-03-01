import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface SystemState {
    numProcesses: number;
    numResources: number;
    processes: string[];
    resources: string[];
    allocation: number[][];
    max: number[][];
    available: number[];
    isConfigured: boolean;
}

interface SystemContextType {
    system: SystemState;
    setSystem: React.Dispatch<React.SetStateAction<SystemState>>;
    generateSystem: (numP: number, numR: number) => void;
    resetSystem: () => void;
}

const defaultState: SystemState = {
    numProcesses: 5,
    numResources: 3,
    processes: ['P0', 'P1', 'P2', 'P3', 'P4'],
    resources: ['A', 'B', 'C'],
    allocation: [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ],
    max: [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ],
    available: [3, 3, 2],
    isConfigured: false,
};

const SystemContext = createContext<SystemContextType | undefined>(undefined);

export function SystemProvider({ children }: { children: ReactNode }) {
    const [system, setSystem] = useState<SystemState>(defaultState);

    const generateSystem = (numP: number, numR: number) => {
        const processes = Array.from({ length: numP }, (_, i) => `P${i}`);
        const resources = Array.from({ length: numR }, (_, i) => String.fromCharCode(65 + i));

        // Generate realistic random data
        const totalPerResource = Array.from({ length: numR }, () => Math.floor(Math.random() * 8) + 4);
        const allocation: number[][] = [];
        const max: number[][] = [];
        const used = new Array(numR).fill(0);

        for (let i = 0; i < numP; i++) {
            const allocRow: number[] = [];
            const maxRow: number[] = [];
            for (let j = 0; j < numR; j++) {
                const maxAlloc = Math.min(totalPerResource[j] - used[j], Math.floor(Math.random() * 4));
                const alloc = Math.floor(Math.random() * (maxAlloc + 1));
                allocRow.push(alloc);
                maxRow.push(alloc + Math.floor(Math.random() * (totalPerResource[j] - alloc + 1)));
                used[j] += alloc;
            }
            allocation.push(allocRow);
            max.push(maxRow);
        }

        const available = totalPerResource.map((total, j) => total - used[j]);

        setSystem({
            numProcesses: numP,
            numResources: numR,
            processes,
            resources,
            allocation,
            max,
            available,
            isConfigured: true,
        });
    };

    const resetSystem = () => setSystem(defaultState);

    return (
        <SystemContext.Provider value={{ system, setSystem, generateSystem, resetSystem }}>
            {children}
        </SystemContext.Provider>
    );
}

export function useSystem() {
    const context = useContext(SystemContext);
    if (!context) {
        throw new Error('useSystem must be used within a SystemProvider');
    }
    return context;
}
