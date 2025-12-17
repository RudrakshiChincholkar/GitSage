import { Routes, Route } from "react-router-dom";
import GitHubAnalyser from "./components/GitHubAnalyser";
import ComparePage from "./components/ComparePage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GitHubAnalyser />} />
      <Route path="/compare" element={<ComparePage />} />
    </Routes>
  );
}
