import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { Home } from './pages/Home';
import { QA } from './pages/QA';
import { Docs } from './pages/Docs';
import { Compare } from './pages/Compare';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen" style={{ backgroundColor: 'var(--background)' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/qa" element={<QA />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/compare" element={<Compare />} />
        </Routes>
      </div>
    </Router>
  );
}
