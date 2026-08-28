import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchCases, fetchHealth, fetchDbHealth, fetchMe } from "../lib/api";
import { Case, User } from "../types/types";

export default function OfficerDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [dbConnected, setDbConnected] = useState<boolean | null>(null);
  
  // Filtering & Search
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");

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
        console.error("Officer dashboard load failed", err);
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
        <p className="font-semibold">Loading officer workspace...</p>
      </div>
    );
  }

  const handleLogout = () => {
    localStorage.removeItem("bhoomiflow_token");
    localStorage.removeItem("bhoomiflow_user");
    navigate("/login");
  };

  const filteredCases = cases.filter((c) => {
    const matchesStatus = statusFilter === "ALL" || c.status === statusFilter;
    const matchesType = typeFilter === "ALL" || c.case_type === typeFilter;
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.case_reference.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.village.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesType && matchesSearch;
  });

  const uniqueCaseTypes = Array.from(new Set(cases.map((c) => c.case_type)));

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <header className="h-16 fixed top-0 w-full bg-white border-b flex justify-between items-center px-6 z-50">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-indigo-700">BhoomiFlow</span>
          <span className="text-slate-400 font-semibold">|</span>
          <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-bold uppercase">
            Officer Workspace
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

      <main className="flex-1 pt-20 pb-16 px-6 max-w-7xl mx-auto w-full">
        {/* Officer Context Card */}
        <div className="bg-white rounded-xl border p-6 my-6 flex justify-between items-center shadow-sm">
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              Welcome, {user?.officer_profile?.full_name}
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Designation: {user?.officer_profile?.designation} • Dept: {user?.officer_profile?.department}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Assigned Jurisdiction: Taluka {user?.officer_profile?.taluka}, District {user?.officer_profile?.district}
            </p>
          </div>
          <div className="text-right text-sm font-semibold">
            <span className="text-indigo-600">{cases.length} Total cases in database</span>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by case ref, title, village..."
              className="w-full max-w-md p-2.5 border rounded-lg bg-white"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex gap-3">
            <div>
              <select
                className="p-2.5 border rounded-lg bg-white text-sm"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">All Statuses</option>
                <option value="SUBMITTED">SUBMITTED</option>
                <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                <option value="ACTION_REQUIRED">ACTION_REQUIRED</option>
                <option value="CLOSED">CLOSED</option>
              </select>
            </div>
            <div>
              <select
                className="p-2.5 border rounded-lg bg-white text-sm max-w-xs"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <option value="ALL">All Categories</option>
                {uniqueCaseTypes.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Case List Queue */}
        <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h3 className="font-bold text-slate-800">Case Queue</h3>
          </div>

          {filteredCases.length > 0 ? (
            <div className="divide-y">
              {filteredCases.map((c) => (
                <div
                  key={c.case_id}
                  onClick={() => navigate(`/cases/${c.case_id}`)}
                  className="px-6 py-4 flex flex-col md:flex-row md:items-center justify-between hover:bg-slate-50 transition-colors cursor-pointer gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded">
                        {c.case_reference}
                      </span>
                      <span className="text-xs text-slate-400">
                        {c.village}, {c.taluka}
                      </span>
                    </div>
                    <h4 className="font-bold text-slate-800">{c.title}</h4>
                    <p className="text-xs text-slate-400">
                      Category: {c.case_type} • Priority: {c.priority}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <span
                      className={`text-xs font-bold px-2.5 py-1 rounded-full ${
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
                    <span className="text-indigo-600 text-sm font-semibold hover:underline">
                      Open →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500">
              <span className="text-4xl block mb-2">📥</span>
              <p className="font-semibold text-slate-600">No cases assigned to you.</p>
              <p className="text-sm text-slate-400 mt-1">
                There are no cases matching the current filters or assigned region.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
