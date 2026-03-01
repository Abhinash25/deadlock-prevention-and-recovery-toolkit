import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SystemProvider } from './lib/SystemContext';
import Sidebar from './components/Sidebar';
import SetupPage from './pages/SetupPage';
import BankersPage from './pages/BankersPage';
import DetectionPage from './pages/DetectionPage';
import RecoveryPage from './pages/RecoveryPage';
import SimulationPage from './pages/SimulationPage';

export default function App() {
  return (
    <SystemProvider>
      <Router>
        <div className="flex min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-500/30">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
            <Routes>
              <Route path="/" element={<SetupPage />} />
              <Route path="/bankers" element={<BankersPage />} />
              <Route path="/detection" element={<DetectionPage />} />
              <Route path="/recovery" element={<RecoveryPage />} />
              <Route path="/simulation" element={<SimulationPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </SystemProvider>
  );
}
