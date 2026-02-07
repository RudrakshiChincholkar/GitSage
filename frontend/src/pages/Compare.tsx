import { useState } from 'react';
import { Github, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { compareRepos, CompareResponse } from "../api/gitsage";

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items || items.length === 0) return null;

  return (
    <div>
      <h4 className="font-medium mb-1">{title}</h4>
      <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function Compare() {
  const [repoUrl1, setRepoUrl1] = useState('');
  const [repoUrl2, setRepoUrl2] = useState('');
  const [isComparing, setIsComparing] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!repoUrl1 || !repoUrl2) return;

    setIsComparing(true);
    setError(null);

    try {
      const data = await compareRepos(repoUrl1, repoUrl2);
      setComparison(data);
      setShowComparison(true);
    } catch (err) {
      setError("Failed to compare repositories");
    } finally {
      setIsComparing(false);
    }
  };

  const FeatureStatusIcon = ({ status }: { status: 'yes' | 'no' | 'partial' }) => {
    if (status === 'yes') {
      return <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--secondary)' }} />;
    }
    if (status === 'no') {
      return <XCircle className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />;
    }
    return <AlertCircle className="w-5 h-5" style={{ color: 'var(--accent)' }} />;
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="border-b" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--card)' }}>
        <div className="max-w-6xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-semibold mb-6">Compare Repositories</h1>
          
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            {/* Repository 1 Input */}
            <div>
              <label className="block text-sm mb-2" style={{ color: 'var(--muted-foreground)' }}>
                First Repository
              </label>
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
                  <Github className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                </div>
                <input
                  type="text"
                  value={repoUrl1}
                  onChange={(e) => setRepoUrl1(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className="w-full h-12 pl-12 pr-4 rounded-xl border-2 transition-all focus:outline-none"
                  style={{
                    borderColor: repoUrl1 ? 'var(--primary)' : 'var(--input-border)',
                    backgroundColor: 'var(--input-background)',
                  }}
                />
              </div>
            </div>

            {/* Repository 2 Input */}
            <div>
              <label className="block text-sm mb-2" style={{ color: 'var(--muted-foreground)' }}>
                Second Repository
              </label>
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
                  <Github className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                </div>
                <input
                  type="text"
                  value={repoUrl2}
                  onChange={(e) => setRepoUrl2(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className="w-full h-12 pl-12 pr-4 rounded-xl border-2 transition-all focus:outline-none"
                  style={{
                    borderColor: repoUrl2 ? 'var(--primary)' : 'var(--input-border)',
                    backgroundColor: 'var(--input-background)',
                  }}
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleCompare}
            disabled={!repoUrl1 || !repoUrl2 || isComparing}
            className="w-full h-12 rounded-xl font-medium transition-all hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
            style={{
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
            }}
          >
            {isComparing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Comparing repositories...
              </>
            ) : (
              'Compare Repositories'
            )}
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {!showComparison ? (
          <div className="text-center py-20">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: 'var(--teal)' + '15' }}
            >
              <svg className="w-8 h-8" style={{ color: 'var(--teal)' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="8.5" cy="7" r="4" />
                <path d="M20 8v6M23 11h-6" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-3">Compare two repositories side by side</h2>
            <p style={{ color: 'var(--muted-foreground)' }}>
              Enter two GitHub repository URLs above to see a detailed comparison
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {error && (
              <div
                className="p-4 rounded-xl border"
                style={{
                  backgroundColor: 'var(--card)',
                  borderColor: 'var(--border)',
                  color: 'var(--destructive)',
                }}
              >
                {error}
              </div>
            )}
            
            {comparison && (
              <>
                {/* Repository Headers */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Repo A */}
                  <div
                    className="p-6 rounded-xl border"
                    style={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)' }}
                  >
                    <h3 className="text-xl font-semibold mb-2">
                      {comparison.repo_a.name}
                    </h3>
                    <p className="text-sm mb-4" style={{ color: 'var(--muted-foreground)' }}>
                      {comparison.repo_a.description || "No description"}
                    </p>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>⭐ Stars: {comparison.repo_a.stars}</div>
                      <div>🍴 Forks: {comparison.repo_a.forks}</div>
                      <div>🧠 Language: {comparison.repo_a.language || "N/A"}</div>
                      <div>📦 Dependencies: {comparison.repo_a.dependencies}</div>
                      <div>📄 License: {comparison.repo_a.license || "N/A"}</div>
                      <div>🕒 Updated: {comparison.repo_a.last_updated || "N/A"}</div>
                    </div>
                  </div>

                  {/* Repo B */}
                  <div
                    className="p-6 rounded-xl border"
                    style={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)' }}
                  >
                    <h3 className="text-xl font-semibold mb-2">
                      {comparison.repo_b.name}
                    </h3>
                    <p className="text-sm mb-4" style={{ color: 'var(--muted-foreground)' }}>
                      {comparison.repo_b.description || "No description"}
                    </p>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>⭐ Stars: {comparison.repo_b.stars}</div>
                      <div>🍴 Forks: {comparison.repo_b.forks}</div>
                      <div>🧠 Language: {comparison.repo_b.language || "N/A"}</div>
                      <div>📦 Dependencies: {comparison.repo_b.dependencies}</div>
                      <div>📄 License: {comparison.repo_b.license || "N/A"}</div>
                      <div>🕒 Updated: {comparison.repo_b.last_updated || "N/A"}</div>
                    </div>
                  </div>
                </div>

                {/* High-Level Comparison */}
                <div
                  className="p-6 rounded-xl border space-y-6"
                  style={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)' }}
                >
                  <h3 className="text-lg font-semibold">High-Level Comparison</h3>

                  <Section
                    title="📌 Overview"
                    items={comparison.overall_comparison.overview || []}
                  />

                  <Section
                    title="🏗 Architecture"
                    items={comparison.overall_comparison.architecture || []}
                  />

                  <div>
                    <h4 className="font-medium mb-2">💪 Strengths</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      <Section
                        title="Repo A"
                        items={comparison.overall_comparison.strengths?.repo_a || []}
                      />
                      <Section
                        title="Repo B"
                        items={comparison.overall_comparison.strengths?.repo_b || []}
                      />
                    </div>
                  </div>

                  <Section
                    title="⚖ Trade-offs"
                    items={comparison.overall_comparison.tradeoffs || []}
                  />

                  <div>
                    <h4 className="font-medium mb-2">🎯 Ideal Use Cases</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      <Section
                        title="Repo A"
                        items={comparison.overall_comparison.ideal_use_cases?.repo_a || []}
                      />
                      <Section
                        title="Repo B"
                        items={comparison.overall_comparison.ideal_use_cases?.repo_b || []}
                      />
                    </div>
                  </div>

                  <Section
                    title="🧠 Final Verdict"
                    items={comparison.overall_comparison.verdict || []}
                  />
                </div>

                {/* Feature Comparison */}
                <div
                  className="p-6 rounded-xl border"
                  style={{
                    backgroundColor: 'var(--card)',
                    borderColor: 'var(--border)',
                  }}
                >
                  <h3 className="text-lg font-semibold mb-6">Feature Comparison</h3>

                  <div className="space-y-3">
                    {Object.entries(comparison.feature_comparison).map(
                      ([featureName, values]) => {
                        const featureValues = values as { repo_a: "yes" | "no" | "partial"; repo_b: "yes" | "no" | "partial" };
                        return (
                          <div
                            key={featureName}
                            className="grid grid-cols-[1fr,auto,auto] gap-4 items-center py-3 border-b last:border-b-0"
                            style={{ borderColor: 'var(--border)' }}
                          >
                            <div className="font-medium">{featureName}</div>

                            <div className="flex justify-center">
                              <FeatureStatusIcon status={featureValues.repo_a} />
                            </div>

                            <div className="flex justify-center">
                              <FeatureStatusIcon status={featureValues.repo_b} />
                            </div>
                          </div>
                        );
                      }
                    )}
                  </div>
                  
                  <div className="mt-6 pt-6 border-t flex items-center gap-6 text-sm" style={{ borderColor: 'var(--border)', color: 'var(--muted-foreground)' }}>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--secondary)' }} />
                      Supported
                    </div>
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                      Partial
                    </div>
                    <div className="flex items-center gap-2">
                      <XCircle className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                      Not supported
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
