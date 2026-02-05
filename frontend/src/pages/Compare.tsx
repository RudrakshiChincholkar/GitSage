import { useState } from 'react';
import { Github, Star, GitFork, Package, Code, Users, Calendar, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

interface ComparisonData {
  name: string;
  description: string;
  stars: number;
  forks: number;
  lastUpdated: string;
  language: string;
  license: string;
  size: string;
  dependencies: number;
  features: {
    name: string;
    status: 'yes' | 'no' | 'partial';
  }[];
}

export function Compare() {
  const [repoUrl1, setRepoUrl1] = useState('');
  const [repoUrl2, setRepoUrl2] = useState('');
  const [isComparing, setIsComparing] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  const handleCompare = () => {
    if (!repoUrl1 || !repoUrl2) return;
    
    setIsComparing(true);
    setTimeout(() => {
      setIsComparing(false);
      setShowComparison(true);
    }, 1500);
  };

  // Mock comparison data
  const comparisonData: [ComparisonData, ComparisonData] = [
    {
      name: 'Repository A',
      description: 'A comprehensive web framework for building modern applications',
      stars: 45200,
      forks: 8300,
      lastUpdated: '2 days ago',
      language: 'TypeScript',
      license: 'MIT',
      size: '12.4 MB',
      dependencies: 42,
      features: [
        { name: 'TypeScript Support', status: 'yes' },
        { name: 'Server-Side Rendering', status: 'yes' },
        { name: 'Hot Module Replacement', status: 'yes' },
        { name: 'Built-in Testing', status: 'partial' },
        { name: 'Mobile Support', status: 'yes' },
        { name: 'GraphQL Integration', status: 'no' },
      ],
    },
    {
      name: 'Repository B',
      description: 'Lightweight and fast web framework with minimal dependencies',
      stars: 38900,
      forks: 5600,
      lastUpdated: '1 week ago',
      language: 'JavaScript',
      license: 'Apache 2.0',
      size: '3.2 MB',
      dependencies: 18,
      features: [
        { name: 'TypeScript Support', status: 'partial' },
        { name: 'Server-Side Rendering', status: 'no' },
        { name: 'Hot Module Replacement', status: 'yes' },
        { name: 'Built-in Testing', status: 'yes' },
        { name: 'Mobile Support', status: 'partial' },
        { name: 'GraphQL Integration', status: 'yes' },
      ],
    },
  ];

  const StatIcon = ({ icon: Icon, label, value1, value2 }: { icon: any; label: string; value1: string | number; value2: string | number }) => (
    <div className="space-y-3">
      <div className="flex items-center gap-2" style={{ color: 'var(--muted-foreground)' }}>
        <Icon className="w-4 h-4" />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div
          className="p-3 rounded-lg text-center"
          style={{ backgroundColor: 'var(--muted)' }}
        >
          <div className="font-semibold">{value1}</div>
        </div>
        <div
          className="p-3 rounded-lg text-center"
          style={{ backgroundColor: 'var(--muted)' }}
        >
          <div className="font-semibold">{value2}</div>
        </div>
      </div>
    </div>
  );

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
            {/* Repository Headers */}
            <div className="grid md:grid-cols-2 gap-6">
              {comparisonData.map((repo, idx) => (
                <div
                  key={idx}
                  className="p-6 rounded-xl border"
                  style={{
                    backgroundColor: 'var(--card)',
                    borderColor: 'var(--border)',
                  }}
                >
                  <h3 className="text-xl font-semibold mb-2">{repo.name}</h3>
                  <p className="text-sm mb-4" style={{ color: 'var(--muted-foreground)' }}>
                    {repo.description}
                  </p>
                  <div className="flex items-center gap-4 text-sm" style={{ color: 'var(--muted-foreground)' }}>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4" />
                      {repo.stars.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <GitFork className="w-4 h-4" />
                      {repo.forks.toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Statistics Comparison */}
            <div
              className="p-6 rounded-xl border"
              style={{
                backgroundColor: 'var(--card)',
                borderColor: 'var(--border)',
              }}
            >
              <h3 className="text-lg font-semibold mb-6">Repository Statistics</h3>
              <div className="space-y-6">
                <StatIcon
                  icon={Code}
                  label="Primary Language"
                  value1={comparisonData[0].language}
                  value2={comparisonData[1].language}
                />
                <StatIcon
                  icon={Package}
                  label="Dependencies"
                  value1={comparisonData[0].dependencies}
                  value2={comparisonData[1].dependencies}
                />
                <StatIcon
                  icon={Calendar}
                  label="Last Updated"
                  value1={comparisonData[0].lastUpdated}
                  value2={comparisonData[1].lastUpdated}
                />
                <StatIcon
                  icon={Users}
                  label="License"
                  value1={comparisonData[0].license}
                  value2={comparisonData[1].license}
                />
              </div>
            </div>

            {/* Features Comparison */}
            <div
              className="p-6 rounded-xl border"
              style={{
                backgroundColor: 'var(--card)',
                borderColor: 'var(--border)',
              }}
            >
              <h3 className="text-lg font-semibold mb-6">Feature Comparison</h3>
              <div className="space-y-3">
                {comparisonData[0].features.map((feature, idx) => (
                  <div
                    key={idx}
                    className="grid grid-cols-[1fr,auto,auto] gap-4 items-center py-3 border-b last:border-b-0"
                    style={{ borderColor: 'var(--border)' }}
                  >
                    <div className="font-medium">{feature.name}</div>
                    <div className="flex justify-center">
                      <FeatureStatusIcon status={feature.status} />
                    </div>
                    <div className="flex justify-center">
                      <FeatureStatusIcon status={comparisonData[1].features[idx].status} />
                    </div>
                  </div>
                ))}
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
          </div>
        )}
      </div>
    </div>
  );
}
