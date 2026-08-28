import { useEffect, useState, FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  fetchCase, 
  fetchCaseEvents, 
  updateCaseStatus, 
  uploadDocument, 
  fetchEvidence, 
  compareDocuments,
  fetchCaseGraph,
  fetchCaseConflicts,
  updateConflictStatus,
  fetchCaseGuidance,
  createEvidenceRequest,
  fetchEvidenceRequests,
  fulfillEvidenceRequest,
  fetchNotifications
} from "../lib/api";
import { Case, CaseEvent, Evidence } from "../types/types";
import { useLanguage } from "../lib/LanguageContext";

const DOCUMENT_TYPES = [
  "Land Record",
  "Sale Deed",
  "Mutation Document",
  "Property Card",
  "Registration Document",
  "Death Certificate",
  "Succession/Legal-Heir Document",
  "Court Order",
  "Survey Document",
  "Application",
  "Other"
];

interface GraphNode {
  id: string;
  type: string;
  label: string;
  details: Record<string, any>;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const [caseObj, setCaseObj] = useState<Case | null>(null);
  const [events, setEvents] = useState<CaseEvent[]>([]);
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [userRole, setUserRole] = useState<string>("citizen");
  
  // Officer status updates
  const [newStatus, setNewStatus] = useState("UNDER_REVIEW");
  const [statusNote, setStatusNote] = useState("");
  const [updating, setUpdating] = useState(false);

  // File Upload states
  const [uploadType, setUploadType] = useState(DOCUMENT_TYPES[0]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState("");

  // Document Comparison states
  const [compDocA, setCompDocA] = useState("");
  const [compDocB, setCompDocB] = useState("");
  const [comparing, setComparing] = useState(false);
  const [compareResult, setCompareResult] = useState<any | null>(null);

  // Phase 3 Graph & Conflict states
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [resolvingConflictId, setResolvingConflictId] = useState("");

  // Phase 4 RAG states
  const [ragQuestion, setRagQuestion] = useState("");
  const [ragAnswer, setRagAnswer] = useState("");
  const [ragSources, setRagSources] = useState<any[]>([]);
  const [ragSearching, setRagSearching] = useState(false);

  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Phase 5 states
  const [evidenceRequests, setEvidenceRequests] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [newRequestDesc, setNewRequestDesc] = useState("");
  const [creatingRequest, setCreatingRequest] = useState(false);
  const [fulfillingRequestId, setFulfillingRequestId] = useState("");

  const loadData = async () => {
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

      const evidence = await fetchEvidence(caseId);
      setEvidenceList(evidence);

      // Load Case Graph representation
      const graphData = await fetchCaseGraph(caseId);
      setGraphNodes(graphData.nodes);
      setGraphEdges(graphData.edges);

      // Load Potential Conflicts
      const conflictList = await fetchCaseConflicts(caseId);
      setConflicts(conflictList);

      // Load Evidence Requests and Notifications
      const requests = await fetchEvidenceRequests(caseId);
      setEvidenceRequests(requests);
      const notifs = await fetchNotifications(caseId);
      setNotifications(notifs);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to load case details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [caseId]);

  const handleStatusChange = async (e: FormEvent) => {
    e.preventDefault();
    if (!caseId) return;
    setUpdating(true);
    setErrorMsg(null);

    try {
      const updated = await updateCaseStatus(caseId, newStatus, statusNote);
      setCaseObj(updated);
      setStatusNote("");
      await loadData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to update case status.");
    } finally {
      setUpdating(false);
    }
  };

  const handleFileUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!caseId || !selectedFile) return;
    setUploading(true);
    setErrorMsg(null);
    setUploadProgress("Uploading file & extracting metadata...");

    try {
      await uploadDocument(caseId, uploadType, selectedFile);
      setUploadProgress("Upload successful!");
      setSelectedFile(null);
      await loadData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "File upload failed.");
      setUploadProgress("");
    } finally {
      setUploading(false);
    }
  };

  const handleCompare = async (e: FormEvent) => {
    e.preventDefault();
    if (!compDocA || !compDocB) return;
    setComparing(true);
    setCompareResult(null);
    setErrorMsg(null);

    try {
      const result = await compareDocuments(compDocA, compDocB);
      setCompareResult(result);
      await loadData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Comparison failed.");
    } finally {
      setComparing(false);
    }
  };

  const handleRagQuery = async (e: FormEvent) => {
    e.preventDefault();
    if (!caseId || !ragQuestion.trim()) return;
    setRagSearching(true);
    setRagAnswer("");
    setRagSources([]);
    setErrorMsg(null);

    try {
      const guidance = await fetchCaseGuidance(caseId, ragQuestion);
      setRagAnswer(guidance.answer);
      setRagSources(guidance.sources);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to retrieve guidance.");
    } finally {
      setRagSearching(false);
    }
  };

  const handleConflictStatus = async (conflictId: string, status: string) => {
    setResolvingConflictId(conflictId);
    try {
      await updateConflictStatus(conflictId, status);
      await loadData();
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to update conflict status.");
    } finally {
      setResolvingConflictId("");
    }
  };

  const handleCreateEvidenceRequest = async (e: FormEvent) => {
    e.preventDefault();
    if (!caseId || !newRequestDesc.trim()) return;
    setCreatingRequest(true);
    setErrorMsg(null);

    try {
      await createEvidenceRequest(caseId, newRequestDesc);
      setNewRequestDesc("");
      await loadData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to create evidence request.");
    } finally {
      setCreatingRequest(false);
    }
  };

  const handleFulfillRequest = async (requestId: string) => {
    setFulfillingRequestId(requestId);
    setErrorMsg(null);

    try {
      await fulfillEvidenceRequest(requestId);
      await loadData();
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to fulfill evidence request.");
    } finally {
      setFulfillingRequestId("");
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
      <header className="h-16 bg-white border-b flex items-center justify-between px-4 md:px-6 sticky top-0 z-45">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(userRole === "officer" ? "/officer" : "/citizen")}
            className="text-sm font-semibold text-indigo-600 hover:underline"
          >
            ← {t("backDashboard")}
          </button>
        </div>
        <div className="text-sm font-bold text-slate-500 truncate max-w-[150px] sm:max-w-none">
          {t("caseLabel")}: {caseObj.case_reference}
        </div>
      </header>

      <main className="max-w-7xl mx-auto w-full mt-8 px-4 md:px-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left/Middle Column: Overview, Documents, Case Graph, and Potential Conflicts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Action Required Widget (Always Visible at Top when requested) */}
          <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-bold border-b pb-2 text-rose-700">{t("requestedEvidence")}</h3>
            {evidenceRequests.length > 0 ? (
              <div className="space-y-3">
                {evidenceRequests.map((req) => (
                  <div key={req.request_id} className="p-4 border rounded-xl bg-rose-50/50 flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{req.description}</p>
                      <span className="text-[10px] text-slate-400 font-mono block mt-1">
                        Requested: {new Date(req.created_at).toLocaleString()} | Status: <strong className={req.status === "OPEN" ? "text-rose-600" : "text-emerald-600"}>{req.status}</strong>
                      </span>
                    </div>
                    {userRole === "citizen" && req.status === "OPEN" && (
                      <button
                        onClick={() => handleFulfillRequest(req.request_id)}
                        disabled={fulfillingRequestId === req.request_id}
                        className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded text-xs font-bold transition-all disabled:opacity-50"
                      >
                        {fulfillingRequestId === req.request_id ? t("btnFulfilling") : t("btnFulfill")}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 italic">{t("noRequestedEvidence")}</p>
            )}

            {/* Officer Action: Request Evidence Form */}
            {userRole === "officer" && (
              <form onSubmit={handleCreateEvidenceRequest} className="border-t pt-4 space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Request Additional Evidence</h4>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newRequestDesc}
                    onChange={(e) => setNewRequestDesc(e.target.value)}
                    placeholder="Enter document request explanation..."
                    className="flex-1 p-2 border rounded text-sm bg-white"
                  />
                  <button
                    type="submit"
                    disabled={creatingRequest || !newRequestDesc.trim()}
                    className="px-4 py-2 bg-rose-600 hover:bg-rose-750 text-white rounded text-sm font-bold transition-all disabled:opacity-50"
                  >
                    {creatingRequest ? "Requesting..." : "Submit Request"}
                  </button>
                </div>
              </form>
            )}
          </div>

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
                  <div key={lp.id} className="text-sm bg-slate-50 p-3 rounded border space-y-1.5 mb-2">
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

          {/* Interactive Case Graph Projection Section */}
          <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Interactive Case Graph Projection</h3>
            
            {graphNodes.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Visual relationship canvas list */}
                <div className="md:col-span-2 border rounded-xl p-4 bg-slate-50 max-h-96 overflow-y-auto space-y-4">
                  <p className="text-xs text-slate-400 italic mb-2">Click any node below to trace details and associated relationships:</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {graphNodes.map((node) => {
                      const colors: Record<string, string> = {
                        CASE: "bg-indigo-100 text-indigo-800 border-indigo-300",
                        PERSON: "bg-emerald-100 text-emerald-800 border-emerald-300",
                        LAND_PARCEL: "bg-amber-100 text-amber-800 border-amber-300",
                        DOCUMENT: "bg-rose-100 text-rose-800 border-rose-300",
                        EVIDENCE: "bg-blue-100 text-blue-800 border-blue-300",
                        EVENT: "bg-slate-100 text-slate-800 border-slate-300"
                      };

                      return (
                        <button
                          key={node.id}
                          onClick={() => setSelectedNode(node)}
                          className={`px-3 py-1.5 rounded-lg border text-xs font-semibold hover:opacity-80 transition-all ${
                            colors[node.type] || "bg-slate-50 text-slate-800"
                          } ${selectedNode?.id === node.id ? "ring-2 ring-indigo-600 ring-offset-1" : ""}`}
                        >
                          {node.type}: {node.label}
                        </button>
                      );
                    })}
                  </div>

                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Active Linkages</h4>
                    {graphEdges.length > 0 ? (
                      <div className="space-y-1 text-xs text-slate-600 font-mono">
                        {graphEdges.map((edge, idx) => {
                          const srcNode = graphNodes.find(n => n.id === edge.source);
                          const targetNode = graphNodes.find(n => n.id === edge.target);
                          return (
                            <div key={idx} className="bg-white p-1 rounded border">
                              {srcNode ? srcNode.label : "Entity"} ──[{edge.type}]──&gt; {targetNode ? targetNode.label : "Entity"}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400 italic">No connections recorded.</p>
                    )}
                  </div>
                </div>

                {/* Node details drawer */}
                <div className="border rounded-xl p-4 bg-white space-y-3">
                  <h4 className="font-bold text-sm text-slate-800 border-b pb-2">Selected Node Trace</h4>
                  {selectedNode ? (
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-400">Node Type</span>
                        <span className="font-bold text-indigo-600">{selectedNode.type}</span>
                      </div>
                      <div className="flex justify-between items-center border-b pb-2">
                        <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-400">Label</span>
                        <span className="font-bold text-slate-850">{selectedNode.label}</span>
                      </div>
                      <div className="space-y-1.5 mt-2">
                        <p className="font-semibold uppercase tracking-wider text-[10px] text-slate-400">Attributes</p>
                        {Object.entries(selectedNode.details).map(([key, val]) => (
                          <div key={key} className="flex flex-col bg-slate-50 p-1.5 rounded border border-slate-100">
                            <span className="text-[10px] text-slate-500 font-semibold">{key}</span>
                            <span className="font-mono break-all">{String(val)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">Click any node to view PostgreSQL-backed attribute trace.</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-400 italic">Graph representation empty.</p>
            )}
          </div>

          {/* Potential Conflicts (Officer Only) */}
          {userRole === "officer" && (
            <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
              <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Potential Verification Conflicts</h3>
              
              {conflicts.length > 0 ? (
                <div className="space-y-3">
                  {conflicts.map((c) => {
                    const badgeColors: Record<string, string> = {
                      OPEN: "bg-rose-50 text-rose-700 border-rose-200",
                      REVIEWED: "bg-blue-50 text-blue-700 border-blue-200",
                      DISMISSED: "bg-slate-100 text-slate-600 border-slate-300"
                    };

                    return (
                      <div key={c.conflict_id} className="p-4 border rounded-xl bg-slate-50 flex flex-col justify-between gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold uppercase tracking-wider bg-rose-100 text-rose-800 px-2 py-0.5 rounded">
                                {c.conflict_type}
                              </span>
                              <span className="text-xs font-semibold uppercase text-slate-400">
                                Severity: {c.severity}
                              </span>
                            </div>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeColors[c.status] || ""}`}>
                              {c.status}
                            </span>
                          </div>

                          <p className="text-sm font-semibold text-slate-800">{c.description}</p>
                          
                          <div className="text-[10px] text-slate-500 space-y-1 font-mono pt-2 border-t border-dashed border-slate-200">
                            <p>Conflict ID: {c.conflict_id}</p>
                            {c.source_entity_a && <p>Source Entity A: {c.source_entity_a}</p>}
                            {c.source_entity_b && <p>Source Entity B: {c.source_entity_b}</p>}
                            <p>Detected At: {new Date(c.detected_at).toLocaleString()}</p>
                            {c.resolved_at && <p>Resolved At: {new Date(c.resolved_at).toLocaleString()}</p>}
                          </div>
                        </div>

                        {c.status === "OPEN" && (
                          <div className="flex items-center gap-2 pt-2 justify-end border-t border-slate-200">
                            <button
                              disabled={resolvingConflictId === c.conflict_id}
                              onClick={() => handleConflictStatus(c.conflict_id, "REVIEWED")}
                              className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-bold transition-all disabled:opacity-50"
                            >
                              Mark Reviewed
                            </button>
                            <button
                              disabled={resolvingConflictId === c.conflict_id}
                              onClick={() => handleConflictStatus(c.conflict_id, "DISMISSED")}
                              className="px-3 py-1 bg-slate-600 hover:bg-slate-700 text-white rounded text-xs font-bold transition-all disabled:opacity-50"
                            >
                              Dismiss
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-slate-600 italic">No potential conflicts detected.</p>
              )}
            </div>
          )}

          {/* Grounded Procedure Guidance RAG Widget */}
          <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Find Government Procedure Guidance</h3>
            <p className="text-xs text-slate-500">
              Search the authoritative state knowledge base for procedures, circulars, and document requirements relevant to this case.
            </p>
            <form onSubmit={handleRagQuery} className="flex gap-2">
              <input
                type="text"
                value={ragQuestion}
                onChange={(e) => setRagQuestion(e.target.value)}
                placeholder="Ask about land mutation timelines, heir certificates, needed documents..."
                className="flex-1 p-2 border rounded text-sm bg-white"
              />
              <button
                type="submit"
                disabled={ragSearching || !ragQuestion}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-bold transition-all disabled:opacity-50"
              >
                {ragSearching ? "Searching..." : "Search Guidance"}
              </button>
            </form>

            {ragAnswer && (
              <div className="p-4 border rounded-xl bg-slate-50 space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-slate-400">Grounded AI explanation</h4>
                <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">{ragAnswer}</p>
                
                {ragSources.length > 0 && (
                  <div className="border-t pt-3 mt-3">
                    <h5 className="font-bold text-[10px] text-slate-450 uppercase tracking-wider mb-2">Sources Cited:</h5>
                    <div className="flex flex-wrap gap-2">
                      {ragSources.map((src, idx) => (
                        <div key={idx} className="bg-white px-2.5 py-1 rounded border text-[10px] space-y-0.5">
                          <span className="font-bold block text-slate-700">{src.title}</span>
                          <span className="text-slate-400 block">{src.department} • Scope: {src.scope}</span>
                          {src.source_url && src.source_url !== "Not available" && (
                            <a
                              href={src.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-indigo-600 hover:underline block font-semibold"
                            >
                              Official Link
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Case Evidence & Documents</h3>
            
            {evidenceList.length > 0 ? (
              <div className="space-y-3">
                {evidenceList.map((ev) => {
                  let meta = null;
                  try {
                    meta = ev.document.extracted_metadata ? JSON.parse(ev.document.extracted_metadata) : null;
                  } catch (e) {
                    console.error("Failed to parse document metadata", e);
                  }

                  return (
                    <div key={ev.evidence_id} className="p-4 border rounded-xl bg-slate-50 flex flex-col md:flex-row justify-between gap-4">
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">
                            {ev.document.document_type}
                          </span>
                          <span className="text-xs text-slate-400 font-semibold uppercase">
                            {ev.evidence_type}
                          </span>
                        </div>
                        <h4 className="font-bold text-slate-800">{ev.document.file_name}</h4>
                        <div className="text-xs text-slate-500 space-y-1">
                          <p className="font-mono">SHA-256: {ev.document.sha256_hash.substring(0, 24)}...</p>
                          <p>Uploaded: {new Date(ev.document.uploaded_at).toLocaleString()}</p>
                          {meta && (
                            <div className="mt-2 p-2 bg-white rounded border border-slate-200">
                              <p className="font-semibold text-slate-700 mb-1">Rule-Extracted Metadata:</p>
                              {meta.issue_date && <p>• Issue Date: {meta.issue_date.value} ({meta.issue_date.source})</p>}
                              {meta.registration_number && <p>• Reg No: {meta.registration_number.value} ({meta.registration_number.source})</p>}
                              {meta.survey_number && <p>• Survey No: {meta.survey_number.value} ({meta.survey_number.source})</p>}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex flex-col items-end justify-between gap-2">
                        <span className="text-xs font-bold uppercase text-emerald-600 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                          {ev.document.status}
                        </span>
                        <a
                          href={`http://localhost:8000/api/v1/documents/${ev.document.document_id}/download`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs font-bold text-indigo-600 hover:underline flex items-center gap-1"
                        >
                          View / Download
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-slate-400 italic">No documents uploaded.</p>
            )}
          </div>

          {/* Document Hashing Comparison Widget (Officer Only) */}
          {userRole === "officer" && evidenceList.length > 1 && (
            <div className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
              <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Evidence Verification Comparison</h3>
              <form onSubmit={handleCompare} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Citizen Submission</label>
                    <select
                      className="w-full p-2 border rounded bg-white text-sm"
                      value={compDocA}
                      onChange={(e) => setCompDocA(e.target.value)}
                    >
                      <option value="">Select Document...</option>
                      {evidenceList
                        .filter((e) => e.evidence_type === "CITIZEN_SUBMISSION")
                        .map((e) => (
                          <option key={e.document.document_id} value={e.document.document_id}>
                            {e.document.file_name} ({e.document.document_id.substring(0, 8)})
                          </option>
                        ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Official Counterpart</label>
                    <select
                      className="w-full p-2 border rounded bg-white text-sm"
                      value={compDocB}
                      onChange={(e) => setCompDocB(e.target.value)}
                    >
                      <option value="">Select Document...</option>
                      {evidenceList
                        .filter((e) => e.evidence_type === "OFFICIAL_COUNTERPART")
                        .map((e) => (
                          <option key={e.document.document_id} value={e.document.document_id}>
                            {e.document.file_name} ({e.document.document_id.substring(0, 8)})
                          </option>
                        ))}
                    </select>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={comparing || !compDocA || !compDocB}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold text-sm disabled:opacity-50"
                >
                  {comparing ? "Comparing Fingerprints..." : "Compare Signatures / Content"}
                </button>
              </form>

              {compareResult && (
                <div className={`p-4 border rounded-xl mt-4 ${compareResult.match ? "bg-emerald-50 border-emerald-200" : "bg-amber-50 border-amber-200"}`}>
                  <h4 className={`font-bold text-sm uppercase ${compareResult.match ? "text-emerald-800" : "text-amber-800"}`}>
                    Verification Result: {compareResult.status_text}
                  </h4>
                  <div className="text-xs text-slate-600 space-y-1.5 mt-2 font-mono">
                    <p>Citizen Fingerprint: {compareResult.citizen_hash}</p>
                    <p>Official Fingerprint: {compareResult.officer_hash}</p>
                  </div>
                  {compareResult.comparison_summary && (
                    <div className="mt-3 pt-3 border-t text-xs text-slate-700 font-sans">
                      <p className="font-semibold">Content Comparison Analysis:</p>
                      <p className="mt-1">{compareResult.comparison_summary}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Side: Timeline, Actions, Upload Panel */}
        <div className="space-y-6">
          {/* Document Upload Widget */}
          <div className="bg-white rounded-xl border p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 border-b pb-2">Attach Document / Evidence</h3>
            <form onSubmit={handleFileUpload} className="space-y-3">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Document Category</label>
                <select
                  className="w-full p-2 border rounded bg-white text-sm"
                  value={uploadType}
                  onChange={(e) => setUploadType(e.target.value)}
                >
                  {DOCUMENT_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Select File (PDF, JPEG, PNG)</label>
                <input
                  type="file"
                  required
                  className="w-full p-1 border rounded bg-white text-sm"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                />
              </div>
              <button
                type="submit"
                disabled={uploading || !selectedFile}
                className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm font-bold transition-colors disabled:opacity-50"
              >
                {uploading ? "Uploading..." : "Upload Evidence"}
              </button>
              {uploadProgress && <p className="text-xs text-indigo-600 mt-1 font-semibold">{uploadProgress}</p>}
            </form>
          </div>

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

          {/* SMS Notification Activity Log */}
          <div className="bg-white rounded-xl border p-6 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-800 border-b pb-2">SMS Notification Logs</h3>
            {notifications.length > 0 ? (
              <div className="space-y-3">
                {notifications.map((n) => (
                  <div key={n.notification_id} className="p-3 border rounded bg-slate-50 text-xs space-y-1">
                    <div className="flex justify-between items-center font-semibold text-slate-700">
                      <span>{n.event_type}</span>
                      <span className={n.status === "SENT" ? "text-emerald-600" : "text-rose-600 font-bold"}>
                        {n.status}
                      </span>
                    </div>
                    <p className="text-slate-650 font-sans">{n.message}</p>
                    <span className="text-[10px] text-slate-400 block font-mono">
                      Sent: {new Date(n.created_at).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-450 italic">No notification alerts triggered for this case.</p>
            )}
          </div>

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
                          {metadata.file_name && <p className="italic text-indigo-600">Attached: {metadata.file_name}</p>}
                        </div>
                      )}
                      {evt.current_event_hash && (
                        <p className="text-[10px] font-mono text-slate-400 mt-1 break-all select-all" title="Append-only cryptographic signature">
                          SIG: {evt.current_event_hash}
                        </p>
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
