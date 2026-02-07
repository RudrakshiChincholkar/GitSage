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
export interface CompareResponse {
  repo_a: {
    name: string;
    description: string;
    stars: number;
    forks: number;
    language: string;
    license: string;
    dependencies: number;
    last_updated: string;
  };
  repo_b: {
    name: string;
    description: string;
    stars: number;
    forks: number;
    language: string;
    license: string;
    dependencies: number;
    last_updated: string;
  };
  overall_comparison: {
    overview: string[];
    architecture: string[];
    strengths: {
      repo_a: string[];
      repo_b: string[];
    };
    tradeoffs: string[];
    ideal_use_cases: {
      repo_a: string[];
      repo_b: string[];
    };
    verdict: string[];
    paragraph: string;
  };
  feature_comparison: Record<
    string,
    {
      repo_a: "yes" | "no" | "partial";
      repo_b: "yes" | "no" | "partial";
    }
  >;
}

export async function compareRepos(
  repoA: string,
  repoB: string
): Promise<CompareResponse> {
  const res = await fetch(`${API_BASE}/compare-repos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repo_a_namespace: repoA,
      repo_b_namespace: repoB,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to compare repositories");
  }

  return res.json();
}
