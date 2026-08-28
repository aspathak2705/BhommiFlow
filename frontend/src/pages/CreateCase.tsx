import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createCase } from "../lib/api";

const CASE_TYPES = [
  "Inheritance / succession",
  "Missing document",
  "Document discrepancy",
  "Document alteration concern",
  "Ownership record conflict",
  "Name / identity variation",
  "Mutation delay",
  "Registration inconsistency",
  "Survey / parcel mismatch",
  "Court order vs land record discrepancy",
  "Other",
];

export default function CreateCase() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  // Form states
  const [caseType, setCaseType] = useState(CASE_TYPES[0]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  
  // Location
  const [district, setDistrict] = useState("");
  const [taluka, setTaluka] = useState("");
  const [village, setVillage] = useState("");

  // Land Context
  const [surveyNumber, setSurveyNumber] = useState("");
  const [subdivisionNumber, setSubdivisionNumber] = useState("");
  const [propertyType, setPropertyType] = useState("Agricultural");
  const [area, setArea] = useState("");
  const [areaUnit, setAreaUnit] = useState("Hectare");
  const [landDescription, setLandDescription] = useState("");

  // People Involved list
  const [people, setPeople] = useState<any[]>([]);
  const [personName, setPersonName] = useState("");
  const [personRole, setPersonRole] = useState("owner");
  const [personPhone, setPersonPhone] = useState("");
  const [personEmail, setPersonEmail] = useState("");
  const [personNotes, setPersonNotes] = useState("");

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const addPerson = () => {
    if (!personName.trim()) return;
    setPeople([
      ...people,
      {
        full_name: personName,
        role: personRole,
        phone: personPhone || undefined,
        email: personEmail || undefined,
        notes: personNotes || undefined,
      },
    ]);
    setPersonName("");
    setPersonPhone("");
    setPersonEmail("");
    setPersonNotes("");
  };

  const removePerson = (index: number) => {
    setPeople(people.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    setErrorMsg(null);
    setLoading(true);

    try {
      const payload = {
        case_type: caseType,
        title,
        description,
        district,
        taluka,
        village,
        land_parcels: [
          {
            district,
            taluka,
            village,
            survey_number: surveyNumber || undefined,
            subdivision_number: subdivisionNumber || undefined,
            property_type: propertyType,
            area: area ? parseFloat(area) : undefined,
            area_unit: areaUnit,
            description: landDescription || undefined,
          },
        ],
        people,
      };

      await createCase(payload);
      navigate("/citizen");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit case.");
      setStep(4); // Keep on Review step
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="h-16 bg-white border-b flex items-center justify-between px-6 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-indigo-700">BhoomiFlow</span>
          <span className="text-slate-400 font-semibold">|</span>
          <span className="text-sm text-slate-600 font-semibold">New Case Intake</span>
        </div>
        <button
          onClick={() => navigate("/citizen")}
          className="text-sm font-semibold text-slate-500 hover:text-slate-800"
        >
          Cancel
        </button>
      </header>

      <main className="max-w-2xl mx-auto w-full mt-10 px-6">
        {/* Step Indicator */}
        <div className="flex justify-between items-center mb-8 text-xs font-bold text-slate-400 uppercase">
          <span className={step >= 1 ? "text-indigo-600" : ""}>1. Profile & Type</span>
          <span className={step >= 2 ? "text-indigo-600" : ""}>2. Land Context</span>
          <span className={step >= 3 ? "text-indigo-600" : ""}>3. People Involved</span>
          <span className={step >= 4 ? "text-indigo-600" : ""}>4. Review & Submit</span>
        </div>

        {errorMsg && (
          <div className="p-3 mb-6 bg-rose-50 border border-rose-200 text-rose-700 rounded text-sm font-medium">
            {errorMsg}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border p-8 space-y-6">
          {/* STEP 1: Case Identity and Type */}
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Define Issue / Category</h3>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Case Category</label>
                <select
                  className="w-full p-2.5 border rounded-lg bg-white"
                  value={caseType}
                  onChange={(e) => setCaseType(e.target.value)}
                >
                  {CASE_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Short Title</label>
                <input
                  type="text"
                  placeholder="e.g. Discrepancy in Mutation Entry for Survey 41"
                  required
                  className="w-full p-2.5 border rounded-lg bg-white"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Original Description</label>
                <textarea
                  rows={5}
                  placeholder="Explain your situation in plain language. Your original description is saved exactly as entered to ensure evidence and provenance integrity."
                  required
                  className="w-full p-2.5 border rounded-lg bg-white"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
            </div>
          )}

          {/* STEP 2: Land Context */}
          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Land & Property Context</h3>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">District</label>
                  <input
                    type="text"
                    required
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Taluka</label>
                  <input
                    type="text"
                    required
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={taluka}
                    onChange={(e) => setTaluka(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Village</label>
                  <input
                    type="text"
                    required
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={village}
                    onChange={(e) => setVillage(e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Survey Number</label>
                  <input
                    type="text"
                    placeholder="Enter survey no. (or 'Not available')"
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={surveyNumber}
                    onChange={(e) => setSurveyNumber(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Subdivision Number</label>
                  <input
                    type="text"
                    placeholder="e.g. 2A"
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={subdivisionNumber}
                    onChange={(e) => setSubdivisionNumber(e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-1">
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Property Type</label>
                  <select
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={propertyType}
                    onChange={(e) => setPropertyType(e.target.value)}
                  >
                    <option value="Agricultural">Agricultural</option>
                    <option value="Non-Agricultural">Non-Agricultural</option>
                    <option value="Residential">Residential</option>
                    <option value="Commercial">Commercial</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Area</label>
                  <input
                    type="number"
                    step="any"
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={area}
                    onChange={(e) => setArea(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Unit</label>
                  <select
                    className="w-full p-2.5 border rounded-lg bg-white"
                    value={areaUnit}
                    onChange={(e) => setAreaUnit(e.target.value)}
                  >
                    <option value="Hectare">Hectare</option>
                    <option value="Acre">Acre</option>
                    <option value="Guntha">Guntha</option>
                    <option value="Sq Ft">Sq Ft</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Land Description</label>
                <input
                  type="text"
                  placeholder="e.g. Located near the eastern boundary of village road"
                  className="w-full p-2.5 border rounded-lg bg-white"
                  value={landDescription}
                  onChange={(e) => setLandDescription(e.target.value)}
                />
              </div>
            </div>
          )}

          {/* STEP 3: People Involved */}
          {step === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Add Involved Persons</h3>
              <div className="p-4 bg-slate-50 border rounded-lg space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Full Name</label>
                    <input
                      type="text"
                      className="w-full p-2 border rounded bg-white text-sm"
                      value={personName}
                      onChange={(e) => setPersonName(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Role / Capacity</label>
                    <select
                      className="w-full p-2 border rounded bg-white text-sm"
                      value={personRole}
                      onChange={(e) => setPersonRole(e.target.value)}
                    >
                      <option value="owner">Owner</option>
                      <option value="heir">Heir</option>
                      <option value="buyer">Buyer</option>
                      <option value="seller">Seller</option>
                      <option value="applicant">Applicant</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Phone</label>
                    <input
                      type="text"
                      className="w-full p-2 border rounded bg-white text-sm"
                      value={personPhone}
                      onChange={(e) => setPersonPhone(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Email</label>
                    <input
                      type="email"
                      className="w-full p-2 border rounded bg-white text-sm"
                      value={personEmail}
                      onChange={(e) => setPersonEmail(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Notes / Relationship Details</label>
                  <input
                    type="text"
                    className="w-full p-2 border rounded bg-white text-sm"
                    value={personNotes}
                    onChange={(e) => setPersonNotes(e.target.value)}
                  />
                </div>

                <button
                  type="button"
                  onClick={addPerson}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-bold"
                >
                  + Add Person
                </button>
              </div>

              {people.length > 0 && (
                <div className="border rounded-lg divide-y bg-white">
                  {people.map((p, idx) => (
                    <div key={idx} className="p-3 flex justify-between items-center text-sm">
                      <div>
                        <span className="font-bold text-slate-800">{p.full_name}</span>
                        <span className="ml-2 text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-600 font-bold uppercase">
                          {p.role}
                        </span>
                        {p.phone && <p className="text-xs text-slate-400 mt-1">Phone: {p.phone}</p>}
                      </div>
                      <button
                        type="button"
                        onClick={() => removePerson(idx)}
                        className="text-xs text-rose-600 font-bold hover:underline"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* STEP 4: Review and Submit */}
          {step === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold border-b pb-2 text-indigo-700">Review Case Submission</h3>
              <div className="p-4 bg-slate-50 border rounded-lg space-y-3 text-sm">
                <div>
                  <span className="block font-bold text-slate-400 uppercase text-[10px]">Case Type</span>
                  <span className="font-semibold">{caseType}</span>
                </div>
                <div>
                  <span className="block font-bold text-slate-400 uppercase text-[10px]">Title</span>
                  <span className="font-semibold">{title}</span>
                </div>
                <div>
                  <span className="block font-bold text-slate-400 uppercase text-[10px]">Description</span>
                  <p className="text-slate-600 whitespace-pre-line mt-1">{description}</p>
                </div>
                <div>
                  <span className="block font-bold text-slate-400 uppercase text-[10px]">Location</span>
                  <span className="font-semibold">
                    {village}, {taluka}, {district}
                  </span>
                </div>
                {surveyNumber && (
                  <div>
                    <span className="block font-bold text-slate-400 uppercase text-[10px]">Land Parcel Detail</span>
                    <span className="font-semibold">
                      Survey: {surveyNumber} (Subdivision: {subdivisionNumber || "None"}), {propertyType} - {area} {areaUnit}
                    </span>
                  </div>
                )}
                <div>
                  <span className="block font-bold text-slate-400 uppercase text-[10px]">People Involved</span>
                  <span className="font-semibold">{people.length} person(s) registered</span>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-4 border-t">
            {step > 1 ? (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="px-5 py-2.5 border rounded-lg font-semibold hover:bg-slate-50 text-slate-700"
              >
                Back
              </button>
            ) : (
              <div></div>
            )}

            {step < 4 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold shadow"
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                disabled={loading || !title || !description || !district || !taluka || !village}
                onClick={handleSubmit}
                className="px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold shadow disabled:opacity-50"
              >
                {loading ? "Submitting..." : "Submit Case"}
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
