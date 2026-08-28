import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchCase, fetchCaseEvents, updateCaseStatus } from "../lib/api";
import { Case, CaseEvent } from "../types/types";

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [caseObj, setCaseObj] = useState<Case | null>(null);
  const [events, setEvents] = useState<CaseEvent[]>([]);
  const [userRole, setUserRole] = useState<string>("citizen");
  
  // Officer status updates
  const [newStatus, setNewStatus] = useState("UNDER_REVIEW");
  const [statusNote, setStatusNote] = useState("");
  const [updating, setUpdating] = useState(false);

  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      if (!caseId) return;
      try {
        const storedUser = localStorage.getItem("bhoomiflow_user");
        if (storedUser) {
          const user = JSON.parse(storedUser);
          setUserRole(user.role);
        }

        const data = await fetchCase(caseId);
        setCaseObj(data);
        setNewStatus(data.status);

        const eventList = await fetchCaseEvents(caseId);
        setEvents(eventList);
      } catch (err: any) {
        console.error(err);
        setErrorMsg(err.message || "Failed to load case details.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [caseId]);

  const handleStatusChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId) return;
    setUpdating(true);
    setErrorMsg(null);

    try {
      const updated = await updateCaseStatus(caseId, newStatus, statusNote);
      setCaseObj(updated);
      setStatusNote("");
      
      // Reload events to refresh timeline
      const eventList = await fetchCaseEvents(caseId);
      setEvents(eventList);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to update case status.");
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-800">
        <p className="font-semibold">Loading case details...</p>
      </div>
    );
  }

  if (errorMsg && !caseObj) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center bg-slate-50 text-slate-850 p-6">
        <div className="max-w-md w-full bg-white p-8 rounded-xl border text-center space-y-4">
          <h2 className="text-xl font-bold text-indigo-700">Error Loading Case</h2>
          <p className="text-sm text-slate-500">{errorMsg}</p>
          <button
            onClick={() => navigate(userRole === "officer" ? "/officer" : "/citizen")}
            className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-bold"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!caseObj) return null;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="h-16 bg-white border-b flex items-center justify-between px-6 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(userRole === "officer" ? "/officer" : "/citizen")}
            className="text-sm font-semibold text-indigo-600 hover:underline"
          >
            ← Back to Dashboard
          </button>
        </div>
        <div className="text-sm font-bold text-slate-500">
          Case: {caseObj.case_reference}
        </div>
      </header>

      <main className="max-w-4xl mx-auto w-full mt-8 px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Side: Case Details */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                  {caseObj.case_type}
                </span>
                <h2 className="text-2xl font-bold text-slate-800 mt-2">{caseObj.title}</h2>
              </div>
              <span
                className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                  caseObj.status === "SUBMITTED"
                    ? "bg-blue-50 text-blue-700"
                    : caseObj.status === "UNDER_REVIEW"
                    ? "bg-amber-50 text-amber-700"
                    : caseObj.status === "ACTION_REQUIRED"
                    ? "bg-rose-50 text-rose-700"
                    : "bg-emerald-50 text-emerald-700"
                }`}
              >
                {caseObj.status}
              </span>
            </div>

            <div className="pt-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Original Description</h4>
              <p className="text-slate-700 mt-1 whitespace-pre-line border-l-2 pl-3 border-indigo-200">
                {caseObj.description}
              </p>
            </div>

            {/* Land Context */}
            <div className="border-t pt-4">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Land / Property Context</h4>
              {caseObj.land_parcels.length > 0 ? (
                caseObj.land_parcels.map((lp) => (
                  <div key={lp.id} className="text-sm bg-slate-50 p-3 rounded border space-y-1.5">
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <span className="block text-[10px] text-slate-400 font-bold uppercase">District</span>
                        <span className="font-semibold">{lp.district}</span>
                      </div>
                      <div>
                        <span className="block text-[10px] text-slate-400 font-bold uppercase">Taluka</span>
                        <span className="font-semibold">{lp.taluka}</span>
                      </div>
                      <div>
                        <span className="block text-[10px] text-slate-400 font-bold uppercase">Village</span>
                        <span className="font-semibold">{lp.village}</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 border-t pt-1.5 mt-1.5">
                      <div>
                        <span className="block text-[10px] text-slate-400 font-bold uppercase">Survey / Sub-div</span>
                        <span className="font-semibold">
                          {lp.survey_number || "N/A"} - {lp.subdivision_number || "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="block text-[10px] text-slate-400 font-bold uppercase">Area</span>
                        <span className="font-semibold">
                          {lp.area ? `${lp.area} ${lp.area_unit}` : "N/A"}
                        </span>
                      </div>
                    </div>
                    {lp.description && (
                      <p className="text-xs text-slate-500 border-t pt-1.5 mt-1.5 italic">
                        Note: {lp.description}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-400">No land parcel details provided.</p>
              )}
            </div>

            {/* People Involved */}
            <div className="border-t pt-4">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">People Involved</h4>
              {caseObj.people.length > 0 ? (
                <div className="space-y-2">
                  {caseObj.people.map((cp) => (
                    <div key={cp.id} className="text-sm flex justify-between items-center bg-slate-50 p-2.5 rounded border">
                      <div>
                        <span className="font-semibold text-slate-800">{cp.person.full_name}</span>
                        <span className="ml-2 text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-bold uppercase">
                          {cp.role}
                        </span>
                      </div>
                      {cp.notes && <span className="text-xs text-slate-500 italic">{cp.notes}</span>}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400">No involved people registered.</p>
              )}
            </div>
          </div>
        </div>

        {/* Right Side: Timeline & Actions */}
        <div className="space-y-6">
          {/* Officer Status Control Panel */}
          {userRole === "officer" && (
            <div className="bg-white rounded-xl border p-6 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-800 border-b pb-2">Status Workflow</h3>
              <form onSubmit={handleStatusChange} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Set Status</label>
                  <select
                    className="w-full p-2 border rounded bg-white text-sm"
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                  >
                    <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                    <option value="ACTION_REQUIRED">ACTION_REQUIRED</option>
                    <option value="CLOSED">CLOSED</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Add Note</label>
                  <textarea
                    rows={2}
                    className="w-full p-2 border rounded bg-white text-sm"
                    value={statusNote}
                    onChange={(e) => setStatusNote(e.target.value)}
                    placeholder="Enter context/reasoning"
                  />
                </div>
                <button
                  type="submit"
                  disabled={updating}
                  className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-bold transition-colors"
                >
                  {updating ? "Saving..." : "Update Workflow Status"}
                </button>
              </form>
            </div>
          )}

          {/* Case Event Timeline */}
          <div className="bg-white rounded-xl border p-6 shadow-sm">
            <h3 className="font-bold text-slate-800 border-b pb-3 mb-4">Timeline Activity</h3>
            {events.length > 0 ? (
              <div className="relative border-l-2 border-indigo-100 pl-4 space-y-5 text-sm">
                {events.map((evt) => {
                  let metadata = null;
                  try {
                    metadata = evt.metadata_json ? JSON.parse(evt.metadata_json) : null;
                  } catch (e) {
                    console.error("Failed to parse event metadata", e);
                  }

                  return (
                    <div key={evt.event_id} className="relative">
                      {/* Timeline dot */}
                      <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-indigo-500 border border-white"></span>
                      
                      <div className="font-semibold text-slate-800 flex justify-between items-center">
                        <span>{evt.event_type}</span>
                        <span className="text-[10px] text-slate-400 font-normal">
                          {new Date(evt.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <p className="text-xs text-slate-500 mt-0.5">
                        By {evt.actor_role} ({evt.actor_id?.substring(0, 8)})
                      </p>

                      {metadata && (
                        <div className="mt-1 p-2 bg-slate-50 rounded border text-xs text-slate-600 space-y-1">
                          {metadata.old_status && (
                            <p>
                              Transitioned status from <span className="font-semibold">{metadata.old_status}</span> →{" "}
                              <span className="font-semibold">{metadata.new_status}</span>
                            </p>
                          )}
                          {metadata.note && <p className="italic">Note: "{metadata.note}"</p>}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No events logged yet.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
