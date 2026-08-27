import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getTeacher, getClasses, getTasks, fetchHealth, fetchDbHealth } from "../lib/api";
import { Class, TeachingTask } from "../types/task";

export default function Workspace() {
  const navigate = useNavigate();
  const [teacherName, setTeacherName] = useState<string>("Teacher");
  const [classes, setClasses] = useState<Class[]>([]);
  const [tasks, setTasks] = useState<TeachingTask[]>([]);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [dbConnected, setDbConnected] = useState<boolean | null>(null);
  const [searchTopic, setSearchTopic] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const health = await fetchHealth();
        setApiOnline(health.status === "ok");
      } catch {
        setApiOnline(false);
      }

      try {
        const dbHealth = await fetchDbHealth();
        setDbConnected(dbHealth.database === "connected");
      } catch {
        setDbConnected(false);
      }

      try {
        const teacherData = await getTeacher("teacher-demo-001");
        setTeacherName(teacherData.name);
      } catch {
        setTeacherName("Guest Teacher");
      }

      try {
        const classesData = await getClasses("teacher-demo-001");
        setClasses(classesData);
        const tasksData = await getTasks("teacher-demo-001");
        setTasks(tasksData);
      } catch (err) {
        console.error("Error loading workspace data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handlePlanClick = (e: React.FormEvent) => {
    e.preventDefault();
    navigate("/create-task", { state: { initialTopic: searchTopic } });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-on-surface">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="font-label-md">Loading teacher workspace...</p>
        </div>
      </div>
    );
  }

  console.log("Classes:", classes.length);

  return (
    <div className="min-h-screen flex flex-col bg-background text-on-background">
      {/* Header */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-margin-desktop h-16 bg-surface-bright border-b border-outline-variant/30 shadow-sm">
        <div className="flex items-center gap-6">
          <h1 className="font-headline-md text-headline-md font-bold text-primary">ShikshaFlow</h1>
          <nav className="hidden md:flex gap-6 ml-8">
            <span className="text-primary font-bold border-b-2 border-primary pb-1 font-label-md text-label-md cursor-pointer">
              My Teaching Space
            </span>
            <span className="text-on-surface-variant hover:text-primary font-label-md text-label-md transition-colors rounded px-2 py-1 cursor-not-allowed opacity-60">
              Lessons
            </span>
            <span className="text-on-surface-variant hover:text-primary font-label-md text-label-md transition-colors rounded px-2 py-1 cursor-not-allowed opacity-60">
              Teaching Graph
            </span>
          </nav>
        </div>

        {/* Health status badges */}
        <div className="flex space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full border border-outline-variant/40 bg-surface-container-low">
            <span className="font-semibold text-on-surface-variant">API:</span>
            {apiOnline === null ? (
              <span className="text-outline">checking...</span>
            ) : apiOnline ? (
              <span className="text-success-green font-bold flex items-center gap-1">● Online</span>
            ) : (
              <span className="text-error font-bold flex items-center gap-1">● Offline</span>
            )}
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full border border-outline-variant/40 bg-surface-container-low">
            <span className="font-semibold text-on-surface-variant">DB:</span>
            {dbConnected === null ? (
              <span className="text-outline">checking...</span>
            ) : dbConnected ? (
              <span className="text-success-green font-bold flex items-center gap-1">● Connected</span>
            ) : (
              <span className="text-error font-bold flex items-center gap-1">● Disconnected</span>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 pt-24 pb-24 px-4 md:px-margin-desktop max-w-container-max mx-auto w-full">
        {/* Hero Section */}
        <section className="mb-16 flex flex-col items-center justify-center text-center max-w-3xl mx-auto mt-8">
          <div className="w-20 h-20 rounded-full bg-primary-container text-on-primary-container mb-6 flex items-center justify-center overflow-hidden shiksha-shadow">
            <span className="material-symbols-outlined text-4xl">person</span>
          </div>
          <h2 className="font-display-lg text-display-lg text-primary mb-4">Good morning, {teacherName}</h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant mb-10 max-w-xl">
            What would you like to explore today? Your AI assistant is ready to help you plan your next lesson.
          </p>

          {/* Prompt input */}
          <form onSubmit={handlePlanClick} className="relative w-full max-w-2xl group">
            <div className="absolute -inset-1 bg-gradient-to-r from-electric-violet to-secondary rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-500"></div>
            <div className="relative flex items-center w-full bg-surface-container-lowest rounded-2xl p-2 border border-outline-variant/50 shiksha-shadow focus-within:border-electric-violet transition-colors">
              <span className="material-symbols-outlined text-electric-violet ml-4 mr-3" style={{ fontVariationSettings: "'FILL' 1" }}>
                auto_awesome
              </span>
              <input
                className="w-full bg-transparent border-none focus:outline-none focus:ring-0 font-body-lg text-body-lg text-on-surface placeholder:text-on-surface-variant/60 py-3"
                placeholder="Tell us what you want to teach..."
                type="text"
                value={searchTopic}
                onChange={(e) => setSearchTopic(e.target.value)}
              />
              <button
                type="submit"
                className="bg-primary hover:bg-primary/90 text-on-primary rounded-xl px-6 py-3 font-label-md text-label-md transition-colors ml-2 flex items-center gap-2 shrink-0"
              >
                Plan <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
          </form>
        </section>

        {/* Bento Grid */}
        <section className="space-y-12">
          <div>
            <h3 className="font-headline-lg text-headline-lg text-on-surface">Your Teaching Space</h3>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Active Classrooms and Saved Drafts</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
            {/* Class Cards */}
            {classes.length > 0 ? (
              classes.map((cls) => (
                <div key={cls.id} className="col-span-1 md:col-span-8 bg-surface-container-lowest rounded-2xl p-6 shiksha-shadow relative overflow-hidden group border border-outline-variant/30 flex flex-col justify-between min-h-[280px]">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none"></div>
                  <div>
                    <span className="bg-diksha-blue/10 text-diksha-blue text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1 border border-diksha-blue/20 w-fit mb-4">
                      <span className="material-symbols-outlined text-[14px]">school</span> Classroom
                    </span>
                    <h4 className="font-headline-lg text-headline-lg text-primary mb-2">{cls.name}</h4>
                    <p className="font-body-lg text-body-lg text-on-surface-variant">Grade {cls.grade} • Section {cls.section} • {cls.primary_language === "mr" ? "Marathi" : cls.primary_language === "hi" ? "Hindi" : "English"} Medium</p>
                  </div>
                  <div className="flex gap-4 items-center mt-6">
                    <button
                      onClick={() => navigate("/create-task")}
                      className="bg-primary text-on-primary font-label-md text-label-md px-6 py-3 rounded-lg hover:bg-primary/90 transition-transform active:scale-95 flex items-center gap-2 shadow-md"
                    >
                      <span className="material-symbols-outlined">add</span> Create New Task
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-1 md:col-span-8 bg-surface-container-lowest rounded-2xl p-8 shiksha-shadow border border-outline-variant/30 border-dashed flex flex-col justify-center items-center text-center min-h-[280px]">
                <span className="material-symbols-outlined text-4xl text-outline mb-4">school</span>
                <h4 className="font-headline-md text-headline-md text-primary mb-2">No classes available</h4>
                <p className="text-on-surface-variant max-w-sm">No classrooms have been assigned to your profile in PostgreSQL yet.</p>
              </div>
            )}

            {/* Side column */}
            <div className="col-span-1 md:col-span-4 flex flex-col gap-gutter">
              <div className="bg-surface-container-lowest rounded-2xl p-5 shiksha-shadow border border-outline-variant/30 flex-1 flex flex-col justify-between">
                <div>
                  <span className="bg-electric-violet text-on-primary text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm w-fit mb-3">
                    <span className="material-symbols-outlined text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                      auto_awesome
                    </span>{" "}
                    AI-Adapted
                  </span>
                  <h5 className="font-headline-md text-headline-md text-on-surface mb-2 leading-tight">Visualizing Fractions</h5>
                  <p className="font-caption text-caption text-on-surface-variant">Interactive grid adapted for Class 7A</p>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="font-caption text-caption text-on-surface-variant flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">schedule</span> 10m setup
                  </span>
                </div>
              </div>

              <div className="bg-surface-container-lowest rounded-2xl p-5 shiksha-shadow border border-outline-variant/30 flex-1 flex flex-col justify-between">
                <div>
                  <span className="bg-diksha-blue text-on-primary text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm w-fit mb-3">
                    <span className="material-symbols-outlined text-[14px]">menu_book</span> Official Resource
                  </span>
                  <h5 className="font-headline-md text-headline-md text-on-surface mb-2 leading-tight">Math Textbook (Std 7)</h5>
                  <p className="font-caption text-caption text-on-surface-variant">Maharashtra State Board Syllabus</p>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="font-caption text-caption text-on-surface-variant flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">visibility</span> View textbook
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Saved Tasks Section */}
        {tasks.length > 0 && (
          <section className="mt-16 space-y-6">
            <h3 className="font-headline-lg text-headline-lg text-on-surface">Your Recent Tasks</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => navigate(`/tasks/${task.id}`)}
                  className="bg-white rounded-xl p-5 border border-outline-variant/40 shadow-sm hover:-translate-y-1 transition-transform cursor-pointer flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <span className="text-xs font-bold uppercase tracking-wider text-primary bg-primary-fixed px-2 py-0.5 rounded">
                        {task.id}
                      </span>
                      <span className="text-xs text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full font-medium">
                        {task.status}
                      </span>
                    </div>
                    <h4 className="font-headline-md text-headline-md text-on-surface mb-1">{task.topic}</h4>
                    <p className="text-sm text-on-surface-variant">{task.subject}</p>
                  </div>
                  <div className="mt-6 flex justify-between items-center text-xs text-outline border-t pt-3">
                    <span>{task.duration_minutes} min • {task.language === "mr" ? "Marathi" : task.language === "hi" ? "Hindi" : "English"}</span>
                    <span className="text-primary font-semibold flex items-center gap-0.5">
                      Open <span className="material-symbols-outlined text-xs">arrow_forward</span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
