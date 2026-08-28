import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import CitizenDashboard from "./pages/CitizenDashboard";
import CreateCase from "./pages/CreateCase";
import OfficerDashboard from "./pages/OfficerDashboard";
import CaseDetail from "./pages/CaseDetail";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/citizen" element={<CitizenDashboard />} />
        <Route path="/citizen/create-case" element={<CreateCase />} />
        <Route path="/officer" element={<OfficerDashboard />} />
        <Route path="/cases/:caseId" element={<CaseDetail />} />
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}
