import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  FileText, AlertTriangle, ShieldCheck, Upload, Layers, CheckCircle2, 
  ArrowLeft, RefreshCw
} from 'lucide-react';

interface BhoomiDocument {
  document_id: string;
  project_id: string;
  parcel_id?: string;
  document_type: string;
  source_type: string;
  file_name: string;
  file_size: number;
  sha256_hash: string;
  document_status: string;
  extraction_status: string;
  uploaded_at: string;
  data_origin: string;
}

interface EvidenceRecord {
  evidence_id: string;
  document_id: string;
  evidence_type: string;
  field_name: string;
  raw_value: string;
  normalized_value?: string;
  confidence: number;
  verification_status: string;
}

interface ConflictSignal {
  conflict_id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  review_required: boolean;
}

export default function EvidenceWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'documents' | 'evidence' | 'conflicts'>('documents');
  const [documents, setDocuments] = useState<BhoomiDocument[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceRecord[]>([]);
  const [conflicts, setConflicts] = useState<ConflictSignal[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);

  // Upload form state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<string>('7/12 Extract');
  const [surveyNo, setSurveyNo] = useState<string>('');

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch Documents
      const docRes = await fetch(`/api/v1/projects/${projectId}/documents`, { headers });
      if (docRes.ok) {
        const docData = await docRes.json();
        setDocuments(docData);
      }

      // Fetch Evidence
      const evRes = await fetch(`/api/v1/projects/${projectId}/evidence`, { headers });
      if (evRes.ok) {
        const evData = await evRes.json();
        setEvidenceList(evData);
      }

      // Fetch Conflicts
      const cnfRes = await fetch(`/api/v1/projects/${projectId}/conflicts`, { headers });
      if (cnfRes.ok) {
        const cnfData = await cnfRes.json();
        setConflicts(cnfData);
      }
    } catch (err) {
      console.error('Failed to load evidence workspace data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !projectId) return;

    setUploading(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', docType);
      formData.append('source_type', 'synthetic');
      if (surveyNo) formData.append('survey_number', surveyNo);

      const res = await fetch(`/api/v1/projects/${projectId}/documents`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (res.ok) {
        setSelectedFile(null);
        setSurveyNo('');
        fetchData();
      }
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6">
      {/* Top Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => navigate('/officer')}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition"
          >
            <ArrowLeft className="w-5 h-5 text-slate-300" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
              Evidence Intelligence Workspace
            </h1>
            <p className="text-xs text-slate-400">Project ID: {projectId} • Grounded Extraction & Signal Audit</p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 rounded-md text-amber-400 text-xs font-mono">
          <span>DATASET INTEGRATION: NOT INTEGRATED</span>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex space-x-2 border-b border-slate-800 mb-6">
        <button
          onClick={() => setActiveTab('documents')}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'documents'
              ? 'border-emerald-500 text-emerald-400 bg-slate-800/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Source Documents ({documents.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('evidence')}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'evidence'
              ? 'border-emerald-500 text-emerald-400 bg-slate-800/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Extracted Evidence ({evidenceList.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('conflicts')}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'conflicts'
              ? 'border-emerald-500 text-emerald-400 bg-slate-800/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Conflict Signals ({conflicts.length})</span>
        </button>
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <RefreshCw className="w-8 h-8 text-emerald-500 animate-spin" />
        </div>
      ) : (
        <>
          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Upload Form */}
              <div className="bg-slate-800/60 rounded-xl p-5 border border-slate-700/50 h-fit">
                <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <Upload className="w-4 h-4 text-emerald-400" />
                  Upload Land Document
                </h2>
                <form onSubmit={handleUpload} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Document Type</label>
                    <select
                      value={docType}
                      onChange={(e) => setDocType(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                    >
                      <option value="7/12 Extract">7/12 Extract</option>
                      <option value="8A Extract">8A Extract</option>
                      <option value="Sale Deed">Sale Deed</option>
                      <option value="Property Card">Property Card</option>
                      <option value="Mutation Record">Mutation Record</option>
                      <option value="Court Order">Court Order</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Survey Number (Optional)</label>
                    <input
                      type="text"
                      placeholder="e.g. 104/A"
                      value={surveyNo}
                      onChange={(e) => setSurveyNo(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Select File (PDF, PNG, JPG)</label>
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20 cursor-pointer"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={!selectedFile || uploading}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2 rounded-lg text-xs transition disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                    {uploading ? 'Processing Extraction...' : 'Upload & Process Document'}
                  </button>
                </form>
              </div>

              {/* Documents List */}
              <div className="lg:col-span-2 space-y-3">
                {documents.length === 0 ? (
                  <div className="bg-slate-800/40 rounded-xl p-8 text-center border border-slate-700/50">
                    <FileText className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">No documents uploaded for this project yet.</p>
                  </div>
                ) : (
                  documents.map((doc) => (
                    <div key={doc.document_id} className="bg-slate-800/60 rounded-xl p-4 border border-slate-700/50 flex items-center justify-between hover:border-slate-600 transition">
                      <div className="flex items-center space-x-3">
                        <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                          <FileText className="w-5 h-5 text-emerald-400" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-sm font-semibold text-white">{doc.file_name}</h3>
                            <span className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono">
                              {doc.document_type}
                            </span>
                            <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono">
                              {doc.data_origin}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mt-0.5">
                            SHA-256: <span className="font-mono text-slate-500">{doc.sha256_hash.substring(0, 16)}...</span> • Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          doc.extraction_status === 'Completed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {doc.extraction_status}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Evidence Tab */}
          {activeTab === 'evidence' && (
            <div className="space-y-4">
              {evidenceList.length === 0 ? (
                <div className="bg-slate-800/40 rounded-xl p-8 text-center border border-slate-700/50">
                  <Layers className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">No normalized evidence records extracted yet.</p>
                </div>
              ) : (
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-800 text-slate-400 font-medium border-b border-slate-700">
                      <tr>
                        <th className="p-3">Field Name</th>
                        <th className="p-3">Raw Value</th>
                        <th className="p-3">Normalized Value</th>
                        <th className="p-3">Confidence</th>
                        <th className="p-3">Verification Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900/60">
                      {evidenceList.map((ev) => (
                        <tr key={ev.evidence_id} className="hover:bg-slate-800/40">
                          <td className="p-3 font-semibold text-white">{ev.evidence_type}</td>
                          <td className="p-3 font-mono text-slate-300">{ev.raw_value}</td>
                          <td className="p-3 font-mono text-emerald-400">{ev.normalized_value || '—'}</td>
                          <td className="p-3">{(ev.confidence * 100).toFixed(0)}%</td>
                          <td className="p-3">
                            <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-[11px]">
                              {ev.verification_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Conflicts Tab */}
          {activeTab === 'conflicts' && (
            <div className="space-y-4">
              {conflicts.length === 0 ? (
                <div className="bg-slate-800/40 rounded-xl p-8 text-center border border-slate-700/50">
                  <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">Zero cross-record conflict signals detected across project documents.</p>
                </div>
              ) : (
                conflicts.map((cnf) => (
                  <div key={cnf.conflict_id} className="bg-slate-800/60 rounded-xl p-5 border border-amber-500/30 flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 mt-1">
                        <AlertTriangle className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-white">{cnf.title}</h3>
                          <span className="text-[10px] bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded font-semibold uppercase">
                            Severity: {cnf.severity}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-1">{cnf.description}</p>
                        <p className="text-[11px] text-amber-400/80 mt-2 italic font-mono">
                          * Signal requires human officer verification before legal conclusion.
                        </p>
                      </div>
                    </div>

                    <span className="bg-slate-900 border border-slate-700 text-slate-300 text-xs px-3 py-1 rounded-md font-mono">
                      Status: {cnf.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
