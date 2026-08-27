import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Workspace from "./pages/Workspace";
import CreateTask from "./pages/CreateTask";
import TaskDetail from "./pages/TaskDetail";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Workspace />} />
        <Route path="/create-task" element={<CreateTask />} />
        <Route path="/tasks/:taskId" element={<TaskDetail />} />
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
