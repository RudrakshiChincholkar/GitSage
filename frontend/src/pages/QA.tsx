import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { RepoInput } from '../components/RepoInput';
import { Send, Bot, User } from 'lucide-react';
import { ingestRepo, askQuestion } from '../api/gitsage';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function QA() {
  const location = useLocation();

  const [repoUrl, setRepoUrl] = useState<string>(location.state?.repoUrl || '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isIngested, setIsIngested] = useState(false); // 🔥 IMPORTANT

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text: string) => { // ADDED
    if (!text.trim() || !repoUrl) return; // ADDED
 // ADDED
    const userMessage: Message = { // ADDED
      id: Date.now().toString(), // ADDED
      role: 'user', // ADDED
      content: text.trim(), // ADDED
      timestamp: new Date(), // ADDED
    }; // ADDED
 // ADDED
    setMessages(prev => [...prev, userMessage]); // ADDED
    setInput(''); // ADDED
    setIsTyping(true); // ADDED
 // ADDED
    try { // ADDED
      const answer = await askQuestion(repoUrl, userMessage.content); // ADDED
 // ADDED
      const assistantMessage: Message = { // ADDED
        id: (Date.now() + 1).toString(), // ADDED
        role: 'assistant', // ADDED
        content: answer, // ADDED
        timestamp: new Date(), // ADDED
      }; // ADDED
 // ADDED
      setMessages(prev => [...prev, assistantMessage]); // ADDED
    } catch { // ADDED
      setMessages(prev => [ // ADDED
        ...prev, // ADDED
        { // ADDED
          id: (Date.now() + 2).toString(), // ADDED
          role: 'assistant', // ADDED
          content: '❌ Error talking to backend.', // ADDED
          timestamp: new Date(), // ADDED
        }, // ADDED
      ]); // ADDED
    } finally { // ADDED
      setIsTyping(false); // ADDED
    } // ADDED
  }; // ADDED

  const handleRepoSubmit = async (url: string) => {
    setRepoUrl(url);
    setMessages([]);
    setIsIngested(false);
    setIsTyping(true);

    try {
      const result = await ingestRepo(url); // ingest ONCE // ADDED
      if (result?.status === 'success') { // ADDED
        setIsIngested(true); // ADDED
      } else { // ADDED
        alert(result?.message || 'Failed to ingest repository'); // ADDED
      } // ADDED
    } catch {
      alert('Failed to ingest repository');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !repoUrl) return; // ADDED
    await sendMessage(input.trim()); // ADDED
  };

  const suggestedQuestions = [
    "What's the main purpose of this repository?",
    "How is the codebase structured?",
    "What data structures are implemented?",
    "How do I set up the project locally?",
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <label className="block text-sm mb-2 text-muted-foreground">
            Repository
          </label>
          <RepoInput
            onSubmit={handleRepoSubmit}
            initialValue={repoUrl}
            buttonText="Load Repository"
          />
        </div>
      </div>

      {/* Chat */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center px-6">
            <div className="max-w-2xl w-full text-center">
              <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center bg-primary/10">
                <MessageSquare className="w-8 h-8 text-primary" />
              </div>

              <h2 className="text-2xl font-semibold mb-3">
                Ask anything about this repository
              </h2>

              <p className="text-muted-foreground">
                {repoUrl
                  ? "I'll analyze the codebase and answer your questions."
                  : "Load a repository to get started."}
              </p>

              {repoUrl && (
                <div className="mt-8 grid grid-cols-2 gap-3">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(q)} // ADDED
                      className="p-4 rounded-lg border text-left text-sm hover:border-primary"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-6 py-8">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map(m => (
                <div
                  key={m.id}
                  className="flex gap-4"
                  style={{ flexDirection: m.role === 'user' ? 'row-reverse' : 'row' }}
                >
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-primary text-white">
                    {m.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className="p-4 rounded-xl max-w-2xl border bg-card">
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex gap-4">
                  <Bot size={20} />
                  <span className="italic text-muted-foreground">Thinking…</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t bg-card">
          <div className="max-w-3xl mx-auto px-6 py-4">
            <form onSubmit={handleSendMessage}>
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  disabled={isTyping} // ADDED
                  placeholder="Ask a question…"
                  className="flex-1 h-12 px-4 rounded-xl border"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isTyping}
                  className="w-12 h-12 rounded-xl bg-primary text-white"
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageSquare(props: any) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}
