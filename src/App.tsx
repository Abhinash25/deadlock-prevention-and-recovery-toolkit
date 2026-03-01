import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SystemProvider } from './lib/SystemContext';
import Sidebar from './components/Sidebar';
import SetupPage from './pages/SetupPage';
import BankersPage from './pages/BankersPage';
import DetectionPage from './pages/DetectionPage';
import RecoveryPage from './pages/RecoveryPage';
import SimulationPage from './pages/SimulationPage';
import RAGVisualizerPage from './pages/RAGVisualizerPage';

export default function App() {
  return (
    <SystemProvider>
      <Router>
        <div className="flex min-h-screen bg-stone-50 text-stone-800 selection:bg-orange-200/60">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-white">
            <Routes>
              <Route path="/" element={<SetupPage />} />
              <Route path="/bankers" element={<BankersPage />} />
              <Route path="/detection" element={<DetectionPage />} />
              <Route path="/recovery" element={<RecoveryPage />} />
              <Route path="/simulation" element={<SimulationPage />} />
              <Route path="/rag-visualizer" element={<RAGVisualizerPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </SystemProvider>
  );
}
