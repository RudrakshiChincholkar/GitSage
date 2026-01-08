import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeftRight } from "lucide-react";

const BACKEND_URL = "http://127.0.0.1:8000";

export default function GitHubAnalyser() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  
// for questions and answers of the web page...
const [question, setQuestion] = useState("");
const [qaList, setQaList] = useState([]);
// ..till here

 const handleSearch = async () => {
  if (!repoUrl) {
    alert("Please enter a GitHub repository URL");
    return;
    
  }

  // Extract owner and repo from URL
  const match = repoUrl.match(/github\.com\/([^/]+)\/([^/]+)/i);

  if (!match) {
    setError("Invalid GitHub repository URL");
    return;
  }

  const owner = match[1];
  const repo = match[2].replace(".git", "").replace("/", "");

  setLoading(true);
  setResult(null); 
  setError("");

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}`
    );

    if (!response.ok) {
      throw new Error("Repository not found");
    }

    const data = await response.json();

    setResult({
      name: data.full_name,
      stars: data.stargazers_count,
      forks: data.forks_count,
      language: data.language,
      description: data.description,
    });
  } catch (err) {
    setError(err.message || "Failed to fetch repository data");
  } finally {
    setLoading(false);
  }
};

// for questions and answers of the web page...
  const handleAskQuestion = () => {
    if (!question.trim()) return;

    let answer = "";
    const q = question.toLowerCase();

    if (q.includes("language")) {
      answer = `This repository is written in ${result.language}.`;
    } else if (q.includes("stars")) {
      answer = `This repository has ${result.stars} stars.`;
    } else if (q.includes("fork")) {
      answer = `This repository has ${result.forks} forks.`;
    } else if (q.includes("about") || q.includes("description")) {
      answer = result.description || "No description available.";
    } else {
      answer =
        "Basic repo info is available. Advanced answers coming soon.";
    }

    //  New Q&A goes on TOP
    setQaList((prev) => [{ question, answer }, ...prev]);
    setQuestion("");
  };

// for jsx
  return (
    <div className="page">
      {/* Top-left title */}
      <div className="header">
      <h1 className="title">GitHub Analyser</h1>

      {/* Compare button */}
      <button
        className="compare-btn"
        onClick={() => navigate("/compare")}
        >
        <ArrowLeftRight size={14} />
        <span>Compare</span>
     </button>
    </div>


      {/* Search button of Github repo */}
      <div className="container">
        <input
          type="text"
          placeholder="https://github.com/user/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                  handleSearch();
            }
          }}
        />

        <button onClick={handleSearch} disabled={loading}>
          {loading ? "Analysing..." : "Search"}
        </button>

        {error && <p className="error">{error}</p>}

        {result && (
          <div className="result">
            <p><b>Name:</b> {result.name}</p>
            <p><b>Stars:</b> {result.stars}</p>
            <p><b>Forks:</b> {result.forks}</p>
            <p><b>Language:</b> {result.language}</p>
            <p><b>Description:</b> {result.description}</p>
          </div>
        )}
      </div>

    {/* Q and A container */}
     <div className="container" style={{ marginTop: "30px" }}>
        <h2>Ask Questions about this Repo</h2>

        <input
          type="text"
          placeholder="Ask a question about this repo..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                  handleAskQuestion();
            }
          }}
        />

        <button onClick={handleAskQuestion} disabled={!result}>
          Ask
        </button>

        {qaList.map((qa, index) => (
          <div key={index} className="qa-item">
            <p><b>Q:</b> {qa.question}</p>
            <p><b>A:</b> {qa.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

