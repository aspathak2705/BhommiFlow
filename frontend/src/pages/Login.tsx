import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser, registerUser } from "../lib/api";

export default function Login() {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [role, setRole] = useState<"citizen" | "officer">("citizen");
  
  // Form fields
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  
  // Officer fields
  const [department, setDepartment] = useState("");
  const [designation, setDesignation] = useState("");
  const [office, setOffice] = useState("");
  const [district, setDistrict] = useState("");
  const [taluka, setTaluka] = useState("");

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      if (isRegister) {
        await registerUser({
          username,
          password,
          role,
          full_name: fullName,
          email: email || undefined,
          phone: phone || undefined,
          department: role === "officer" ? department : undefined,
          designation: role === "officer" ? designation : undefined,
          office: role === "officer" ? office : undefined,
          district: role === "officer" ? district : undefined,
          taluka: role === "officer" ? taluka : undefined,
        });
        setIsRegister(false);
        setErrorMsg("Registration successful. Please log in.");
      } else {
        const data = await loginUser({ username, password });
        localStorage.setItem("bhoomiflow_token", data.access_token);
        localStorage.setItem("bhoomiflow_user", JSON.stringify(data.user));

        if (data.user.role === "citizen") {
          navigate("/citizen");
        } else {
          navigate("/officer");
        }
      }
    } catch (err: any) {
      setErrorMsg(err.message || "An error occurred during authentication.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-900 px-4">
      <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-md border border-slate-200">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-extrabold text-indigo-700 tracking-tight">BhoomiFlow</h1>
          <p className="text-sm text-slate-500 mt-2">
            Evidence-traceability and case-orchestration portal
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 mb-4 rounded bg-rose-50 border border-rose-200 text-rose-700 text-sm font-medium">
            {errorMsg}
          </div>
        )}

        <div className="flex border-b border-slate-200 mb-6">
          <button
            onClick={() => setIsRegister(false)}
            className={`flex-1 pb-3 text-center font-semibold text-sm ${
              !isRegister ? "border-b-2 border-indigo-600 text-indigo-600" : "text-slate-400"
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setIsRegister(true)}
            className={`flex-1 pb-3 text-center font-semibold text-sm ${
              isRegister ? "border-b-2 border-indigo-600 text-indigo-600" : "text-slate-400"
            }`}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Username</label>
            <input
              type="text"
              required
              className="w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Password</label>
            <input
              type="password"
              required
              className="w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {isRegister && (
            <>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Role</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-sm text-slate-700">
                    <input
                      type="radio"
                      name="role"
                      checked={role === "citizen"}
                      onChange={() => setRole("citizen")}
                    />
                    Citizen
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-700">
                    <input
                      type="radio"
                      name="role"
                      checked={role === "officer"}
                      onChange={() => setRole("officer")}
                    />
                    Government Officer
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  className="w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Email</label>
                <input
                  type="email"
                  className="w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Phone</label>
                <input
                  type="text"
                  className="w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>

              {role === "officer" && (
                <div className="p-3 bg-slate-50 border rounded-lg space-y-3">
                  <h3 className="text-xs font-bold text-slate-600">Officer Context</h3>
                  <div>
                    <label className="block text-[10px] font-bold uppercase text-slate-400">Department</label>
                    <input
                      type="text"
                      className="w-full p-1.5 border rounded text-sm bg-white"
                      value={department}
                      placeholder="e.g. Land Records"
                      onChange={(e) => setDepartment(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase text-slate-400">Designation</label>
                    <input
                      type="text"
                      className="w-full p-1.5 border rounded text-sm bg-white"
                      value={designation}
                      placeholder="e.g. Talathi"
                      onChange={(e) => setDesignation(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase text-slate-400">Office</label>
                    <input
                      type="text"
                      className="w-full p-1.5 border rounded text-sm bg-white"
                      value={office}
                      placeholder="e.g. Taluka Office"
                      onChange={(e) => setOffice(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[10px] font-bold uppercase text-slate-400">District</label>
                      <input
                        type="text"
                        className="w-full p-1.5 border rounded text-sm bg-white"
                        value={district}
                        placeholder="e.g. Pune"
                        onChange={(e) => setDistrict(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase text-slate-400">Taluka</label>
                      <input
                        type="text"
                        className="w-full p-1.5 border rounded text-sm bg-white"
                        value={taluka}
                        placeholder="e.g. Haveli"
                        onChange={(e) => setTaluka(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold shadow-md transition-colors disabled:opacity-50"
          >
            {loading ? "Please wait..." : isRegister ? "Register Account" : "Access Workspace"}
          </button>
        </form>
      </div>
    </div>
  );
}
