import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import CaseDetail from "./pages/CaseDetail";
import Troubleshoot from "./pages/Troubleshoot";
import RuleChecker from "./pages/RuleChecker";
import ResponsibleAI from "./pages/ResponsibleAI";

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <h1>NetSage AI</h1>
          <p>Lab helper for Packet Tracer troubleshooting. AI is a suggestion, not the last word.</p>
        </div>
        <nav>
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/cases">Cases</NavLink>
          <NavLink to="/troubleshoot">Troubleshoot</NavLink>
          <NavLink to="/checker">Rule checker</NavLink>
          <NavLink to="/responsible-ai">Responsible AI</NavLink>
        </nav>
        <p className="side-note">College lab project. Every diagnosis stays pending until a person reviews it.</p>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/cases/:caseId" element={<CaseDetail />} />
          <Route path="/troubleshoot" element={<Troubleshoot />} />
          <Route path="/checker" element={<RuleChecker />} />
          <Route path="/responsible-ai" element={<ResponsibleAI />} />
        </Routes>
      </main>
    </div>
  );
}
