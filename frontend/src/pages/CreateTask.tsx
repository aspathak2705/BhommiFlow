import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { createTask, getClasses } from "../lib/api";
import { Class, TeachingTask } from "../types/task";

export default function CreateTask() {
  const location = useLocation();
  const navigate = useNavigate();
  const initialTopic = location.state?.initialTopic || "";

  // State for class/subject parameters
  const [selectedClass, setSelectedClass] = useState("class-7a");
  const [selectedSubject, setSelectedSubject] = useState("Mathematics");
  const [topic, setTopic] = useState(initialTopic || "Fractions");
  const [duration, setDuration] = useState(40);
  const [language, setLanguage] = useState<"mr" | "hi" | "en">("mr");

  // Flow control states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdTask, setCreatedTask] = useState<TeachingTask | null>(null);
  const [classes, setClasses] = useState<Class[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadClasses() {
      try {
        const data = await getClasses("teacher-demo-001");
        setClasses(data);
      } catch (err) {
        console.error("Failed to load classes:", err);
      }
    }
    loadClasses();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const task = await createTask({
        teacher_id: "teacher-demo-001",
        class_id: selectedClass,
        subject: selectedSubject,
        topic: topic,
        duration_minutes: duration,
        language: language,
      });
      // Show confirmation screen
      setCreatedTask(task);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "We couldn't save your teaching task.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render Confirmation Screen state
  if (createdTask) {
    return (
      <div className="bg-background text-on-surface min-h-screen flex flex-col justify-center items-center relative overflow-hidden selection:bg-primary selection:text-on-primary">
        {/* Ambient background blur */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
          <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-primary-container/20 rounded-full blur-[100px] animate-pulse"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-[60vw] h-[60vw] bg-secondary-container/10 rounded-full blur-[120px] animate-pulse"></div>
        </div>

        {/* Main Content Canvas */}
        <main className="w-full max-w-2xl px-6 md:px-margin-desktop z-10 flex flex-col items-center">
          {/* AI Pulse Indicator */}
          <div className="relative w-32 h-32 mb-8 flex justify-center items-center">
            <div className="absolute w-full h-full bg-electric-violet/20 rounded-full orb-pulse"></div>
            <div className="absolute w-24 h-24 bg-electric-violet/40 rounded-full orb-pulse"></div>
            <div className="relative w-16 h-16 bg-primary rounded-full flex justify-center items-center shadow-lg shadow-primary/30 z-10">
              <span className="material-symbols-outlined text-on-primary text-3xl">check</span>
            </div>
          </div>

          {/* Confirmation Text */}
          <div className="text-center mb-10 animate-fade-in">
            <h1 className="font-display-lg text-display-lg text-on-surface mb-4">Your teaching task is ready.</h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-md mx-auto">
              AI has mapped the context and synthesized the initial structure. We are ready to explore resources.
            </p>
          </div>

          {/* Context Recap Card */}
          <div className="w-full bg-surface-bright/85 backdrop-blur-md border border-outline-variant/30 rounded-3xl p-6 mb-10 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-8 -translate-y-1/2 bg-electric-violet text-on-primary font-caption text-caption px-3 py-1 rounded-full flex items-center gap-1 shadow-sm">
              <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
              AI-Synthesized
            </div>
            <div className="flex flex-col md:flex-row gap-6">
              {/* Data Points */}
              <div className="flex-1 space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary-container/30 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-primary">school</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider text-xs">Topic</p>
                    <p className="font-headline-md text-headline-md text-on-surface">{createdTask.topic}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-secondary-container/30 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-secondary">group</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider text-xs">Class Context</p>
                    <p className="font-body-md text-body-md text-on-surface">
                      Class 7A • Marathi • {createdTask.duration_minutes} min
                    </p>
                  </div>
                </div>
              </div>

              {/* Vertical Divider */}
              <div className="hidden md:block w-px bg-outline-variant/30"></div>

              {/* Projected Goals */}
              <div className="flex-1 space-y-3">
                <p className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider text-xs">Objectives</p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 font-body-md text-body-md text-on-surface">
                    <span className="material-symbols-outlined text-success-green text-[20px]">check_circle</span>
                    Identify learning outcomes
                  </li>
                  <li className="flex items-center gap-2 font-body-md text-body-md text-on-surface">
                    <span className="material-symbols-outlined text-success-green text-[20px]">check_circle</span>
                    Map core terminology
                  </li>
                  <li className="flex items-center gap-2 font-body-md text-body-md text-outline-variant">
                    <span className="material-symbols-outlined text-[20px] animate-pulse">pending</span>
                    Search DIKSHA repository
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Primary CTA */}
          <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
            <button
              onClick={() => navigate(`/tasks/${createdTask.id}`)}
              className="shimmer relative flex items-center justify-center gap-3 bg-primary text-on-primary font-headline-md text-headline-md px-10 py-5 rounded-2xl shadow-lg shadow-primary/20 hover:shadow-xl transition-all"
            >
              <span>View teaching task</span>
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="bg-surface-bright text-on-surface min-h-screen flex flex-col">
      {/* Top Bar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-margin-desktop h-16 bg-surface-bright border-b shadow-sm">
        <div className="flex items-center gap-4">
          <button
            aria-label="Go Back"
            onClick={() => navigate("/")}
            className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center w-10 h-10 rounded-full hover:bg-surface-container-low"
          >
            <span className="material-symbols-outlined">arrow_back</span>
          </button>
          <h1 className="font-headline-md text-headline-md font-bold text-primary">ShikshaFlow</h1>
        </div>
        <div>
          <button
            onClick={() => navigate("/")}
            className="px-6 py-2 rounded-full font-label-md text-label-md bg-surface-container-high text-on-surface-variant hover:bg-surface-container-highest transition-colors"
          >
            Cancel
          </button>
        </div>
      </header>

      {/* Main Progressive form */}
      <main className="pt-24 pb-32 px-4 md:px-margin-desktop max-w-container-max mx-auto w-full flex flex-col items-center">
        {/* Workflow Header */}
        <div className="text-center mb-12 max-w-2xl mx-auto">
          <h2 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-4">
            Design Your Lesson
          </h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            Let's build a focused learning journey. Select the parameters below to generate your interactive teaching graph.
          </p>
        </div>

        {errorMsg && (
          <div className="w-full max-w-4xl p-4 mb-6 border border-error bg-red-50 text-error rounded-xl text-center font-medium">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Steps */}
        <form onSubmit={handleSubmit} className="w-full max-w-4xl space-y-8">
          {/* Step 1: Target Audience */}
          <section className="bg-white rounded-xl shadow-sm border border-outline-variant/30 p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-label-md text-label-md">
                1
              </div>
              <h3 className="font-headline-md text-headline-md text-on-surface">Target Audience</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Class */}
              <div>
                <label className="font-label-md text-label-md text-on-surface-variant block mb-3">Select Class</label>
                <div className="grid grid-cols-3 gap-3">
                  {classes.map((cls) => (
                    <button
                      key={cls.id}
                      type="button"
                      onClick={() => setSelectedClass(cls.id)}
                      className={`py-3 rounded-lg border text-center transition-all ${
                        selectedClass === cls.id
                          ? "border-2 border-primary bg-primary-container/20 text-primary font-bold shadow-sm"
                          : "border-outline-variant/30 hover:bg-surface-container-low text-on-surface"
                      }`}
                    >
                      {cls.name}
                    </button>
                  ))}
                  {classes.length === 0 && (
                    <button
                      type="button"
                      className="py-3 rounded-lg border border-outline-variant/30 text-center bg-surface-container-low text-on-surface"
                    >
                      Class 7A
                    </button>
                  )}
                </div>
              </div>
              {/* Subject */}
              <div>
                <label className="font-label-md text-label-md text-on-surface-variant block mb-3">Select Subject</label>
                <div className="grid grid-cols-2 gap-3">
                  {["Mathematics", "Science"].map((sub) => (
                    <button
                      key={sub}
                      type="button"
                      onClick={() => setSelectedSubject(sub)}
                      className={`flex items-center justify-center gap-2 py-3 rounded-lg border text-center transition-all ${
                        selectedSubject === sub
                          ? "border-2 border-primary bg-primary-container/20 text-primary font-bold shadow-sm"
                          : "border-outline-variant/30 hover:bg-surface-container-low text-on-surface"
                      }`}
                    >
                      <span className="material-symbols-outlined text-[20px]">
                        {sub === "Mathematics" ? "calculate" : "science"}
                      </span>
                      {sub}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Step 2: Topic & Language */}
          <section className="bg-surface-container-lowest rounded-xl shadow-sm border border-primary/10 p-6 md:p-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none"></div>
            <div className="flex items-center gap-3 mb-6 relative z-10">
              <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-label-md text-label-md">
                2
              </div>
              <h3 className="font-headline-md text-headline-md text-on-surface">Topic Context</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 relative z-10">
              {/* Topic Input */}
              <div className="md:col-span-7">
                <label className="font-label-md text-label-md text-on-surface-variant block mb-3">Core Topic</label>
                <div className="relative group">
                  <input
                    className="w-full bg-surface-bright border-2 border-primary/20 rounded-xl px-5 py-4 font-headline-md text-headline-md text-on-surface focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all shadow-inner"
                    placeholder="e.g. Introduction to Fractions"
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    required
                  />
                </div>
              </div>
              {/* Language Selection */}
              <div className="md:col-span-5">
                <label className="font-label-md text-label-md text-on-surface-variant block mb-3">Instruction Language</label>
                <div className="bg-surface-bright rounded-xl border border-outline-variant/30 p-2 flex">
                  {([
                    { code: "en", label: "English" },
                    { code: "mr", label: "Marathi" },
                    { code: "hi", label: "Hindi" },
                  ] as const).map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      onClick={() => setLanguage(lang.code)}
                      className={`flex-1 py-3 rounded-lg text-center transition-all ${
                        language === lang.code
                          ? "bg-white text-primary font-bold shadow-sm relative border border-outline-variant/30"
                          : "text-on-surface-variant hover:bg-surface-container-low"
                      }`}
                    >
                      {lang.label}
                      {language === lang.code && (
                        <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-success-green"></span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Step 3: Duration */}
          <section className="bg-white rounded-xl shadow-sm border border-outline-variant/30 p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-surface-container-highest text-on-surface flex items-center justify-center font-label-md text-label-md">
                3
              </div>
              <h3 className="font-headline-md text-headline-md text-on-surface">Time & Structure</h3>
            </div>
            <div>
              <div className="flex justify-between items-end mb-4">
                <label className="font-label-md text-label-md text-on-surface-variant block">Class Duration</label>
                <span className="font-headline-lg text-headline-lg text-primary">
                  {duration} <span className="font-body-md text-body-md text-on-surface-variant">min</span>
                </span>
              </div>
              {/* Interactive Duration Slider */}
              <input
                type="range"
                min="15"
                max="60"
                step="5"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full h-2 bg-surface-container-high rounded-full appearance-none cursor-pointer accent-primary focus:outline-none"
              />
              <div className="flex justify-between font-caption text-caption text-outline px-1 mt-4">
                <span>15m</span>
                <span>30m</span>
                <span className="text-primary font-bold">40m</span>
                <span>60m</span>
              </div>
            </div>
          </section>

          {/* Floating Action Button */}
          <div className="fixed bottom-0 left-0 w-full bg-surface-bright/95 backdrop-blur-md border-t border-outline-variant/20 p-4 md:p-6 flex justify-center z-40 shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-3 bg-primary text-on-primary px-8 py-4 rounded-xl font-label-md text-label-md shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 disabled:opacity-50"
            >
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                generating_tokens
              </span>
              {isSubmitting ? "Saving task..." : "Generate Teaching Graph"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
