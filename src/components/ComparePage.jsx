import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ComparePage() {
  const navigate = useNavigate();

  // Dynamic list of repo URLs (start with 2)
  const [repos, setRepos] = useState(["", ""]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  

//    URL validation helper
  const isValidGitHubUrl = (url) => {
  return /github\.com\/[^/]+\/[^/]+/i.test(url.trim());
};
  const validRepoCount = repos.filter(
    (r) => r.trim() !== "" && isValidGitHubUrl(r)
  ).length;

const isCompareEnabled = validRepoCount >= 2 && !loading;

  // Extract owner & repo
  const extractRepo = (url) => {
    const match = url.match(/github\.com\/([^/]+)\/([^/]+)/i);
    if (!match) return null;

    return {
      owner: match[1],
      repo: match[2].replace(".git", "").replace("/", ""),
    };
  };

  // Compare all repos
  const handleCompare = async () => {
    setError("");
    setResults([]);

    // Remove empty inputs
    const validRepos = repos.filter((r) => r.trim() !== "");

    if (validRepos.length < 2) {
      setError("Please enter at least two repository URLs");
      return;
    }

    setLoading(true);

    try {
      const data = await Promise.all(
        validRepos.map(async (url) => {
          const parsed = extractRepo(url);
          if (!parsed) {
            throw new Error("Invalid GitHub repository URL");
          }

          const res = await fetch(
            `https://api.github.com/repos/${parsed.owner}/${parsed.repo}`
          );

          if (!res.ok) {
            throw new Error("One or more repositories not found");
          }

          return res.json();
        })
      );

      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Reset everything
  const handleCompareMore = () => {
    setRepos(["", ""]);
    setResults([]);
    setError("");
  };

  return (
    <div className="page">
      {/* Header */}
      <div className="header">
        <h1 className="title">Compare Repositories</h1>

        <button className="compare-btn" onClick={() => navigate("/")}>
          Exit
        </button>
      </div>

      {/* Repo inputs */}
      <div className="container">
        {repos.map((repo, index) => (
          <input
            key={index}
            type="text"
            placeholder={`GitHub repository URL ${index + 1}`}
            value={repo}
            onChange={(e) => {
              const updated = [...repos];
              updated[index] = e.target.value;
              setRepos(updated);
            }}
            // for enter key improovement.
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleCompare();
              }
            }}
            style={{ marginBottom: "10px" }}
          />
        ))}

        <button
          style={{ marginBottom: "10px" }}
          onClick={() => setRepos([...repos, ""])}
        >
          + Add another repository
        </button>

        <button onClick={handleCompare} disabled={isCompareEnabled}>
          {loading ? "Comparing..." : 'Press Enter or click to compare'}
        </button>

        {error && <p className="error">{error}</p>}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="compare-result">
          {results.map((repo) => (
            <div key={repo.id} className="compare-card">
              <h3>{repo.full_name}</h3>
              <p>⭐ Stars: {repo.stargazers_count}</p>
              <p>🍴 Forks: {repo.forks_count}</p>
              <p>🧠 Language: {repo.language}</p>
              <p>{repo.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Compare more */}
      {results.length > 0 && (
        <button
          style={{ marginTop: "20px" }}
          onClick={handleCompareMore}
        >
          Compare more repositories
        </button>
      )}
    </div>
  );
}
