import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { RepoInput } from '../components/RepoInput';
import { generateDocumentation, ingestRepo } from '../api/gitsage';
import { FileText, Package, Settings, Code, BookOpen, Layers } from 'lucide-react';



interface DocSection {
  id: string;
  title: string;
  icon: any;
  content: string;
}

export function Docs() {
  const location = useLocation();
  const [repoUrl, setRepoUrl] = useState(location.state?.repoUrl || '');
  const [isGenerated, setIsGenerated] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [documentation, setDocumentation] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [isIngested, setIsIngested] = useState(false);  

  const handleRepoSubmit = async (url: string) => {
  setRepoUrl(url);
  setIsGenerated(false);
  setError('');
  setIsIngested(false);
  
  // Auto-ingest when repository is loaded
  try {
    setIsGenerating(true);
    const result = await ingestRepo(url);
    if (result?.status === 'success') {
      setIsIngested(true);
    } else {
      setError(result?.message || 'Failed to ingest repository');
    }
  } catch (err) {
    setError('Failed to load repository. Please try again.');
  } finally {
    setIsGenerating(false);
  }
};

  const handleGenerate = async () => {
  if (!repoUrl) return;
  
  setIsGenerating(true);
  setError('');
  
  try {
    const result = await generateDocumentation(repoUrl);
    
    if (result.status === 'success') {
      setDocumentation(result.sections);
      setIsGenerated(true);
    } else {
      setError(result.message || 'Failed to generate documentation');
    }
  } catch (err) {
    setError('Failed to generate documentation. Please try again.');
  } finally {
    setIsGenerating(false);
  }
};

  // Map backend documentation to UI sections
const docSections: DocSection[] = documentation ? [
  {
    id: 'overview',
    title: 'Overview',
    icon: FileText,
    content: documentation.overview || 'No overview available.',
  },
  {
    id: 'architecture',
    title: 'Architecture',
    icon: Layers,
    content: documentation.architecture || 'No architecture information available.',
  },
  {
    id: 'setup',
    title: 'Getting Started',
    icon: Settings,
    content: documentation.setup || 'No setup instructions available.',
  },
  {
    id: 'features',
    title: 'Key Features',
    icon: Code,
    content: documentation.features || 'No features documented.',
  },
  {
    id: 'dependencies',
    title: 'Dependencies',
    icon: Package,
    content: documentation.dependencies || 'No dependency information available.',
  },
  {
    id: 'api',
    title: 'API Reference',
    icon: BookOpen,
    content: documentation.api_reference || 'No API reference available.',
  },
] : [];

  return (
    <div className="min-h-screen">
      {/* Header with Repo Input */}
      <div className="border-b" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--card)' }}>
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="mb-2">
            <label className="block text-sm mb-2" style={{ color: 'var(--muted-foreground)' }}>
              Repository
            </label>
          </div>
          <div className="flex gap-3">
            <div className="flex-1">
              <RepoInput
                onSubmit={handleRepoSubmit}
                initialValue={repoUrl}
                buttonText="Load Repository"
              />
              {error && (
                <div className="mt-4 p-4 rounded-lg border border-red-300 bg-red-50">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}
            </div>
            {repoUrl && (
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="px-6 h-12 rounded-xl font-medium transition-all hover:opacity-90 disabled:opacity-70 flex items-center gap-2"
                style={{
                  backgroundColor: 'var(--secondary)',
                  color: 'var(--secondary-foreground)',
                }}
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    Generate Docs
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        {!repoUrl ? (
          <div className="text-center py-20">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: 'var(--secondary)' + '15' }}
            >
              <BookOpen className="w-8 h-8" style={{ color: 'var(--secondary)' }} />
            </div>
            <h2 className="text-2xl font-semibold mb-3">Generate comprehensive documentation</h2>
            <p style={{ color: 'var(--muted-foreground)' }}>
              Load a repository above to automatically create detailed docs
            </p>
          </div>
        ) : !isGenerated ? (
          <div className="text-center py-20">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
              style={{ backgroundColor: 'var(--secondary)' + '15' }}
            >
              <FileText className="w-8 h-8" style={{ color: 'var(--secondary)' }} />
            </div>
            <h2 className="text-2xl font-semibold mb-3">Ready to generate documentation</h2>
            <p className="mb-6" style={{ color: 'var(--muted-foreground)' }}>
              Click "Generate Docs" above to create comprehensive documentation for this repository
            </p>
            <div className="max-w-md mx-auto">
              <div
                className="p-4 rounded-lg border text-left text-sm space-y-2"
                style={{ borderColor: 'var(--border)', backgroundColor: 'var(--muted)' }}
              >
                <p className="font-medium">Documentation will include:</p>
                <ul className="space-y-1" style={{ color: 'var(--muted-foreground)' }}>
                  <li>• Project overview and purpose</li>
                  <li>• Architecture and design patterns</li>
                  <li>• Setup and installation instructions</li>
                  <li>• API reference and examples</li>
                  <li>• Contributing guidelines</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div>
            {/* Header */}
            <div className="mb-12 pb-8 border-b" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: 'var(--secondary)' }}
                >
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-semibold">Repository Documentation</h1>
                </div>
              </div>
              <p style={{ color: 'var(--muted-foreground)' }}>
                Auto-generated documentation for {repoUrl}
              </p>
            </div>

            {/* Documentation Sections */}
            <div className="space-y-8">
              {docSections.map((section) => {
                const Icon = section.icon;
                return (
                  <div key={section.id} id={section.id}>
                    <div className="flex items-center gap-3 mb-4">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: 'var(--primary)' + '15' }}
                      >
                        <Icon className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                      </div>
                      <h2 className="text-2xl font-semibold">{section.title}</h2>
                    </div>
                    <div
                      className="pl-11 prose prose-sm max-w-none"
                      style={{ color: 'var(--foreground)' }}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{section.content}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Footer */}
            <div
              className="mt-12 pt-8 border-t text-center"
              style={{ borderColor: 'var(--border)' }}
            >
              <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
                Documentation generated on {new Date().toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
