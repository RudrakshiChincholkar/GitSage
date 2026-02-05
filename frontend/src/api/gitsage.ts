const API_BASE = "http://127.0.0.1:8000";

export async function ingestRepo(repoUrl: string) {
  const res = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  if (!res.ok) {
    throw new Error("Failed to ingest repository");
  }

  const data = await res.json(); // ADDED
  return data; // ADDED
}

export async function askQuestion(repoUrl: string, question: string) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repo_url: repoUrl,
      question: question,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to ask question");
  }

  const data = await res.json();
  // backend returns { answer: string }
  return data?.answer ?? data;
}

export async function generateDocumentation(repoUrl: string) {
  const res = await fetch(`${API_BASE}/generate-docs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  if (!res.ok) {
    throw new Error("Failed to generate documentation");
  }

  return res.json();
}