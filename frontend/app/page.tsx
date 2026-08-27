"use client";

import { useEffect, useState } from "react";
import { fetchHealth, fetchDbHealth, HealthResponse, DbHealthResponse } from "../lib/api";

export default function Home() {
  const [apiHealth, setApiHealth] = useState<HealthResponse | null>(null);
  const [dbHealth, setDbHealth] = useState<DbHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [lessonPrompt, setLessonPrompt] = useState("");

  useEffect(() => {
    async function checkHealth() {
      try {
        const healthRes = await fetchHealth();
        setApiHealth(healthRes);
      } catch (err) {
        console.error("API Health error:", err);
      }

      try {
        const dbRes = await fetchDbHealth();
        setDbHealth(dbRes);
      } catch (err) {
        console.error("DB Health error:", err);
      }
      setLoading(false);
    }
    checkHealth();
  }, []);

  const handleBuildLesson = (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("Phase 1 coming soon! Artificial Intelligence lesson generation is locked for Phase 0.");
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header / Navbar */}
      <header className="border-b border-border bg-white px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center space-x-8">
          <h1 className="text-2xl font-bold text-primary font-sans tracking-wide">ShikshaFlow</h1>
          <nav className="hidden md:flex space-x-6 text-sm font-medium">
            <span className="text-foreground/80 cursor-not-allowed hover:text-primary transition-colors">My Classes</span>
            <span className="text-foreground/80 cursor-not-allowed hover:text-primary transition-colors">Lessons</span>
            <span className="text-foreground/80 cursor-not-allowed hover:text-primary transition-colors">Graph</span>
          </nav>
        </div>

        {/* Health status badges */}
        <div className="flex space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full border border-border bg-[#F9FAFB]">
            <span className="font-semibold text-gray-600">API:</span>
            {loading ? (
              <span className="text-gray-400">checking...</span>
            ) : apiHealth ? (
              <span className="text-emerald-600 font-bold">● Running</span>
            ) : (
              <span className="text-rose-600 font-bold">● Offline</span>
            )}
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full border border-border bg-[#F9FAFB]">
            <span className="font-semibold text-gray-600">DB:</span>
            {loading ? (
              <span className="text-gray-400">checking...</span>
            ) : dbHealth && dbHealth.database === "connected" ? (
              <span className="text-emerald-600 font-bold">● Connected</span>
            ) : (
              <span className="text-rose-600 font-bold">● Disconnected</span>
            )}
          </div>
        </div>
      </header>

      {/* Main workspace */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 max-w-4xl mx-auto w-full text-center">
        <div className="w-full space-y-8 animate-fade-in">
          <div className="space-y-3">
            <h2 className="text-4xl md:text-5xl font-extrabold text-foreground tracking-tight leading-tight">
              Good morning, Teacher 👋
            </h2>
            <p className="text-lg md:text-xl text-foreground/70 max-w-xl mx-auto font-indic">
              What are you teaching today?
            </p>
          </div>

          <form onSubmit={handleBuildLesson} className="max-w-2xl mx-auto w-full space-y-6">
            <div className="relative group">
              <input
                type="text"
                value={lessonPrompt}
                onChange={(e) => setLessonPrompt(e.target.value)}
                placeholder="✨ Tell us what you want to teach..."
                className="w-full px-6 py-4 md:py-5 rounded-2xl border-2 border-primary/20 focus:border-primary bg-white text-foreground shadow-md focus:shadow-lg focus:outline-none transition-all pr-12 text-base placeholder:text-gray-400"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none group-focus-within:text-primary transition-colors text-xl">
                ✍️
              </span>
            </div>

            <div>
              <button
                type="submit"
                className="px-8 py-3.5 rounded-xl bg-accent text-accent-foreground font-semibold text-base shadow-md hover:bg-accent/90 hover:shadow-lg active:scale-98 transition-all inline-flex items-center space-x-2"
              >
                <span>Build my lesson</span>
                <span>→</span>
              </button>
            </div>
          </form>

          {/* Feedback/Placeholder message */}
          {message && (
            <div className="max-w-md mx-auto p-4 rounded-xl border border-warning bg-amber-50 text-amber-900 text-sm font-medium shadow-sm animate-bounce-short">
              ⚠️ {message}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-foreground/45 border-t border-border mt-auto">
        ShikshaFlow v0.1.0 (Phase 0 — Foundation Shell)
      </footer>
    </div>
  );
}
