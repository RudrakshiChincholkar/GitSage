import { Link, useLocation } from 'react-router-dom';
import { BookOpen, MessageSquare, GitCompare, Home } from 'lucide-react';

export function Navigation() {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/qa', label: 'Q&A', icon: MessageSquare },
    { path: '/docs', label: 'Docs', icon: BookOpen },
    { path: '/compare', label: 'Compare', icon: GitCompare },
  ];

  return (
    <nav className="border-b" style={{ borderColor: 'var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--primary)' }}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 2L3 6V14L10 18L17 14V6L10 2Z" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
                <path d="M10 10L3 6M10 10L17 6M10 10V18" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="font-semibold text-lg">Gitsage</span>
          </div>
          
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
                  style={{
                    color: active ? 'var(--primary)' : 'var(--muted-foreground)',
                    backgroundColor: active ? 'var(--muted)' : 'transparent',
                  }}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
