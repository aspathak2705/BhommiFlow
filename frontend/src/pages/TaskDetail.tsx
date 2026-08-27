import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTask, updateTask } from "../lib/api";
import { TeachingTask } from "../types/task";

export default function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  const [task, setTask] = useState<TeachingTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Form states for editing
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState(45);
  const [language, setLanguage] = useState<"mr" | "hi" | "en">("mr");
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    async function loadTask() {
      if (!taskId) return;
      try {
        const data = await getTask(taskId);
        setTask(data);
        // Initialize form
        setSubject(data.subject);
        setTopic(data.topic);
        setDuration(data.duration_minutes);
        setLanguage(data.language as any);
      } catch (err: any) {
        console.error(err);
        setErrorMsg(err.message || "Failed to load task details.");
      } finally {
        setLoading(false);
      }
    }
    loadTask();
  }, [taskId]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskId) return;
    setIsUpdating(true);
    setErrorMsg(null);

    try {
      const updated = await updateTask(taskId, {
        subject,
        topic,
        duration_minutes: duration,
        language,
      });
      setTask(updated);
      setIsEditing(false);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "We couldn't save your changes.");
    } finally {
      setIsUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-on-surface">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="font-label-md">Loading your teaching task...</p>
        </div>
      </div>
    );
  }

  if (errorMsg && !task) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center bg-background text-on-surface p-6">
        <div className="max-w-md w-full bg-white p-8 rounded-2xl border border-outline-variant/30 shadow-sm text-center space-y-6">
          <span className="material-symbols-outlined text-error text-5xl">warning</span>
          <h2 className="font-headline-md text-primary">Error Loading Task</h2>
          <p className="text-on-surface-variant">{errorMsg}</p>
          <button
            onClick={() => navigate("/")}
            className="w-full bg-primary text-on-primary py-3 rounded-lg font-bold"
          >
            Go back to Workspace
          </button>
        </div>
      </div>
    );
  }

  if (!task) return null;

  return (
    <div className="min-h-screen flex flex-col bg-background text-on-background">
      {/* Header */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-margin-desktop h-16 bg-surface-bright border-b shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/")}
            className="text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 font-label-md text-label-md hover:bg-surface-container-low px-3 py-1.5 rounded-full"
          >
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            My Teaching Space
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 pt-24 pb-24 px-4 md:px-margin-desktop max-w-4xl mx-auto w-full">
        {errorMsg && (
          <div className="p-4 mb-6 border border-error bg-red-50 text-error rounded-xl text-center font-medium">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Task Card */}
        <div className="bg-white rounded-3xl p-6 md:p-8 border border-outline-variant/40 shadow-sm space-y-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/5 rounded-full blur-3xl pointer-events-none"></div>

          {/* Title Area */}
          <div className="flex justify-between items-start border-b pb-6">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-primary bg-primary-container/20 px-3 py-1 rounded-full mb-3 inline-block">
                {task.id}
              </span>
              <h2 className="font-display-lg text-display-lg text-primary mb-1">{task.topic}</h2>
              <p className="text-on-surface-variant font-body-lg">
                Class 7A • {task.subject} • {task.duration_minutes}m • {task.language === "mr" ? "Marathi" : task.language === "hi" ? "Hindi" : "English"}
              </p>
            </div>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 border border-primary text-primary px-4 py-2 rounded-lg font-label-md hover:bg-primary/5 transition-colors"
              >
                <span className="material-symbols-outlined text-[18px]">edit</span>
                Edit Task
              </button>
            )}
          </div>

          {/* Edit Form / Task Detail Display */}
          {isEditing ? (
            <form onSubmit={handleUpdate} className="space-y-6 animate-fade-in">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-on-surface-variant mb-2">Subject</label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    required
                    className="w-full bg-surface-bright border border-outline-variant/50 rounded-xl px-4 py-3 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-on-surface-variant mb-2">Topic</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    required
                    className="w-full bg-surface-bright border border-outline-variant/50 rounded-xl px-4 py-3 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-on-surface-variant mb-2">Duration (minutes)</label>
                  <input
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    required
                    min="1"
                    className="w-full bg-surface-bright border border-outline-variant/50 rounded-xl px-4 py-3 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-on-surface-variant mb-2">Language</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value as any)}
                    className="w-full bg-surface-bright border border-outline-variant/50 rounded-xl px-4 py-3 text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value="mr">Marathi</option>
                    <option value="hi">Hindi</option>
                    <option value="en">English</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-4 pt-4 border-t justify-end">
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="px-6 py-2.5 rounded-lg border border-outline-variant bg-white text-on-surface-variant"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="px-6 py-2.5 rounded-lg bg-primary text-on-primary font-bold disabled:opacity-50"
                >
                  {isUpdating ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              {/* Context display info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-surface-container-low rounded-xl">
                  <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1">
                    Learning Context
                  </h4>
                  <p className="font-headline-md text-primary">{task.subject}</p>
                  <p className="text-sm text-on-surface-variant mt-1">Class 7A • Grade 7</p>
                </div>
                <div className="p-4 bg-surface-container-low rounded-xl">
                  <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1">
                    Teaching Language
                  </h4>
                  <p className="font-headline-md text-primary">
                    {task.language === "mr" ? "Marathi" : task.language === "hi" ? "Hindi" : "English"}
                  </p>
                  <p className="text-sm text-on-surface-variant mt-1">Duration: {task.duration_minutes} minutes</p>
                </div>
              </div>

              {/* Next Steps Placeholder */}
              <div className="pt-8 border-t border-outline-variant/20">
                <h3 className="font-headline-md text-on-surface mb-4">Government resources</h3>
                <div className="bg-surface-container-low border border-dashed border-outline-variant/60 rounded-2xl p-6 text-center space-y-3">
                  <span className="material-symbols-outlined text-outline text-4xl">cloud_sync</span>
                  <p className="font-label-md text-on-surface-variant">DIKSHA resources are coming next</p>
                  <p className="text-xs text-outline">
                    Phase 2 will integrate official government repository resources here.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
