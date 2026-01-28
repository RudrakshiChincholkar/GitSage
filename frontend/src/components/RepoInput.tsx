import { useState } from 'react';
import { Github } from 'lucide-react';

interface RepoInputProps {
  onSubmit?: (url: string) => void;
  placeholder?: string;
  buttonText?: string;
  initialValue?: string;
}

export function RepoInput({ 
  onSubmit, 
  placeholder = "https://github.com/username/repository",
  buttonText = "Continue",
  initialValue = ""
}: RepoInputProps) {
  const [url, setUrl] = useState(initialValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && onSubmit) {
      onSubmit(url.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <Github className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
          </div>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={placeholder}
            className="w-full h-12 pl-12 pr-4 rounded-xl border-2 transition-all focus:outline-none"
            style={{
              borderColor: url ? 'var(--primary)' : 'var(--input-border)',
              backgroundColor: 'var(--input-background)',
            }}
          />
        </div>
        <button
          type="submit"
          className="px-6 h-12 rounded-xl font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: 'var(--primary)',
            color: 'var(--primary-foreground)',
          }}
        >
          {buttonText}
        </button>
      </div>
    </form>
  );
}
