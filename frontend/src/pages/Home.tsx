import { RepoInput } from '../components/RepoInput';
import { MessageSquare, BookOpen, GitCompare, Sparkles, Zap, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Home() {
  const navigate = useNavigate();

  const handleRepoSubmit = (url: string) => {
    console.log('Repository submitted:', url);
    navigate('/qa', { state: { repoUrl: url } });
  };

  const features = [
    {
      icon: MessageSquare,
      title: 'Ask Questions',
      description: 'Get instant answers about any repository. Understand complex codebases through natural conversation.',
      color: 'var(--primary)',
    },
    {
      icon: BookOpen,
      title: 'Generate Documentation',
      description: 'Create comprehensive docs automatically. Architecture diagrams, API references, and setup guides.',
      color: 'var(--secondary)',
    },
    {
      icon: GitCompare,
      title: 'Compare Repositories',
      description: 'Make informed decisions. See side-by-side comparisons of features, dependencies, and approaches.',
      color: 'var(--teal)',
    },
  ];

  const benefits = [
    { icon: Sparkles, text: 'Understand unfamiliar codebases in minutes, not hours' },
    { icon: Zap, text: 'Onboard new team members with auto-generated documentation' },
    { icon: Shield, text: 'Make better library choices with detailed comparisons' },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto px-6 pt-20 pb-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-semibold mb-6 leading-tight" style={{ color: 'var(--foreground)' }}>
            Understand any GitHub repository,{' '}
            <span style={{ color: 'var(--primary)' }}>without reading every line</span>
          </h1>
          <p className="text-xl mb-4" style={{ color: 'var(--muted-foreground)' }}>
            Gitsage helps developers quickly understand, document, and compare repositories through intelligent Q&A.
          </p>
          <p className="text-lg" style={{ color: 'var(--muted-foreground)' }}>
            Paste a GitHub URL to get started.
          </p>
        </div>

        <div className="mb-8">
          <RepoInput 
            onSubmit={handleRepoSubmit} 
            buttonText="Explore Repository"
          />
        </div>

        <div className="text-center">
          <button
            className="text-sm hover:underline"
            style={{ color: 'var(--primary)' }}
            onClick={() => {
              document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            See how it works →
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div id="how-it-works" className="py-20" style={{ backgroundColor: 'var(--muted)' }}>
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-semibold mb-4">Three ways to understand repositories</h2>
            <p style={{ color: 'var(--muted-foreground)' }}>
              Choose the approach that fits your workflow
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="p-8 rounded-xl border-2"
                  style={{
                    backgroundColor: 'var(--card)',
                    borderColor: 'var(--border)',
                  }}
                >
                  <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
                    style={{ backgroundColor: feature.color + '15' }}
                  >
                    <Icon className="w-6 h-6" style={{ color: feature.color }} />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                  <p style={{ color: 'var(--muted-foreground)' }}>{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="py-20">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-semibold mb-8 text-center">Why developers use Gitsage</h2>
          <div className="space-y-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <div
                  key={index}
                  className="flex items-start gap-4 p-6 rounded-xl border"
                  style={{
                    backgroundColor: 'var(--card)',
                    borderColor: 'var(--border)',
                  }}
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: 'var(--accent)' + '20' }}
                  >
                    <Icon className="w-5 h-5" style={{ color: 'var(--accent)' }} />
                  </div>
                  <p className="text-lg pt-1.5">{benefit.text}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16" style={{ backgroundColor: 'var(--muted)' }}>
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-semibold mb-6">Ready to dive in?</h2>
          <p className="text-lg mb-8" style={{ color: 'var(--muted-foreground)' }}>
            Paste any public GitHub repository URL to start exploring
          </p>
          <div className="max-w-2xl mx-auto">
            <RepoInput 
              onSubmit={handleRepoSubmit} 
              buttonText="Get Started"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
