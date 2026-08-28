import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchCases, fetchHealth, fetchDbHealth, fetchMe } from "../lib/api";
import { Case, User } from "../types/types";

export default function CitizenDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [dbConnected, setDbConnected] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const h = await fetchHealth();
        setApiOnline(h.status === "ok");
      } catch {
        setApiOnline(false);
      }

      try {
        const dbh = await fetchDbHealth();
        setDbConnected(dbh.database === "connected");
      } catch {
        setDbConnected(false);
      }

      try {
        const profile = await fetchMe();
        setUser(profile);
        const casesList = await fetchCases();
        setCases(casesList);
      } catch (err) {
        console.error("Dashboard load failed", err);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-800">
        <p className="font-semibold">Loading citizen workspace...</p>
      </div>
    );
  }

  const handleLogout = () => {
    localStorage.removeItem("bhoomiflow_token");
    localStorage.removeItem("bhoomiflow_user");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <header className="h-16 fixed top-0 w-full bg-white border-b flex justify-between items-center px-6 z-50">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-indigo-700">BhoomiFlow</span>
          <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold uppercase">
            Citizen
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold">
          <div className="flex items-center gap-1.5 px-3 py-1.5 border rounded-full bg-slate-50">
            <span className="text-slate-500">API:</span>
            <span className={apiOnline ? "text-emerald-600" : "text-rose-600"}>
              {apiOnline ? "● Online" : "● Offline"}
            </span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 border rounded-full bg-slate-50">
            <span className="text-slate-500">DB:</span>
            <span className={dbConnected ? "text-emerald-600" : "text-rose-600"}>
              {dbConnected ? "● Connected" : "● Disconnected"}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 border rounded-full hover:bg-slate-100 transition-colors"
          >
            Log Out
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full pt-24 pb-16 px-6">
        <div className="bg-gradient-to-r from-indigo-700 to-violet-800 text-white rounded-2xl p-8 mb-8 shadow-sm">
          <h2 className="text-2xl font-bold">Namaste, {user?.citizen_profile?.full_name}</h2>
          <p className="text-slate-200 mt-2 max-w-xl">
            BhoomiFlow connects your land records, transactions, and evidence into structured cases
            to track resolution. Submit a new case using the portal below.
          </p>
          <button
            onClick={() => navigate("/citizen/create-case")}
            className="mt-6 px-6 py-3 bg-white text-indigo-700 font-bold rounded-lg shadow hover:bg-slate-100 transition-colors"
          >
            Create New Case
          </button>
        </div>

        <h3 className="text-xl font-bold mb-4">My Submitted Cases</h3>

        {cases.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cases.map((c) => (
              <div
                key={c.case_id}
                onClick={() => navigate(`/cases/${c.case_id}`)}
                className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:border-indigo-400 transition-colors cursor-pointer flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-xs font-bold bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                      {c.case_reference}
                    </span>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                        c.status === "SUBMITTED"
                          ? "bg-blue-50 text-blue-700"
                          : c.status === "UNDER_REVIEW"
                          ? "bg-amber-50 text-amber-700"
                          : c.status === "ACTION_REQUIRED"
                          ? "bg-rose-50 text-rose-700"
                          : "bg-emerald-50 text-emerald-700"
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <h4 className="font-bold text-slate-800 text-lg mb-1">{c.title}</h4>
                  <p className="text-sm text-slate-500 line-clamp-2">{c.description}</p>
                </div>
                <div className="mt-4 pt-3 border-t text-xs text-slate-400 flex justify-between">
                  <span>
                    Location: {c.village}, {c.taluka}
                  </span>
                  <span className="text-indigo-600 font-semibold hover:underline">View Details →</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-dashed rounded-2xl p-12 text-center text-slate-500">
            <span className="text-4xl block mb-2">📁</span>
            <p className="font-semibold text-slate-600">No cases yet.</p>
            <p className="text-sm text-slate-400 mt-1">Submit your first land-record dispute or update request.</p>
          </div>
        )}
      </main>
    </div>
  );
}
