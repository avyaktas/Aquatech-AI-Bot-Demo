import React, { useEffect, useMemo, useRef, useState } from "react";
import "./style.css";

type Role = "user" | "assistant" | "system";
interface Message { role: Role; content: string; id?: string }

const useFallbackLogo = true;
const AquatechLogo: React.FC<{ className?: string }> = ({ className = "" }) => (
  useFallbackLogo ? (
    <div className={`aq-logo ${className}`}>
      <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2S5 9.2 5 13.5 8.1 20 12 20s7-2.9 7-6.5S12 2 12 2Z" fill="none" stroke="currentColor" strokeWidth="1.6"/>
        <circle cx="12" cy="15" r="3.2" fill="currentColor"/>
      </svg>
      <span>Aquatech AI Assistant</span>
    </div>
  ) : (
    <img src="/aquatech.svg" alt="Aquatech" className={`aq-logo-img ${className}`} />
  )
);

const WELCOME: Message = {
  role: "assistant",
  content: "Hello! How can I assist you today?",
};

export default function CATUI() {
  const API_BASE = useMemo(() => (import.meta as any)?.env?.VITE_API_BASE || window.location.origin, []);

  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  async function sendMessage() {
    const q = input.trim();
    if (!q || loading) return;
    setError("");
    setLoading(true);
    setMessages(prev => [...prev, { role: "user", content: q, id: crypto.randomUUID() }]);
    setInput("");

    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const text = await res.text();
      if (!res.ok) throw new Error(text || `HTTP ${res.status}`);
      if (text.trim().startsWith("<")) throw new Error("Received HTML from /api/query — check Nginx mapping.");
      const data = JSON.parse(text);
      setMessages(prev => [...prev, { role: "assistant", content: data.answer || "(no answer)", id: crypto.randomUUID() }]);
    } catch (e: any) {
      setError(e?.message || "Request failed");
      setMessages(prev => [...prev, { role: "assistant", content: "Sorry—something went wrong reaching the backend.", id: crypto.randomUUID() }]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function clearChat() { setMessages([WELCOME]); }

  return (
    <div className="aq-shell">
      <div className="aq-card">
        <header className="aq-header">
          <AquatechLogo />
          <div className="aq-header-actions">
            <button className="aq-btn ghost" onClick={clearChat} title="Clear chat">Clear</button>
            <a className="aq-btn cyan" href="/">Home</a>
          </div>
        </header>

        <main className="aq-chat">
          {messages.map((m) => (
            <Bubble key={m.id || Math.random()} role={m.role} text={m.content} />
          ))}
          {loading && <TypingDots />}
          <div ref={endRef} />
        </main>

        <footer className="aq-composer">
          <textarea
            className="aq-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="Ask a question about your docs… (Shift+Enter = newline)"
          />
          <button className="aq-btn send" onClick={sendMessage} disabled={loading || !input.trim()}>
            <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 21l21-9L2 3l3 7 10 2-10 2-3 7z" fill="currentColor"/></svg>
            Send
          </button>
        </footer>
      </div>
    </div>
  );
}

function Bubble({ role, text }: { role: Role; text: string }) {
  const isUser = role === "user";
  return (
    <div className={`aq-row ${isUser ? "end" : "start"}`}>
      <div className={`aq-bubble ${isUser ? "user" : "bot"}`}>{text}</div>
    </div>
  );
}

function TypingDots() {
  return (
    <div className="aq-typing">
      <span className="dot" />
      <span className="dot" />
      <span className="dot" />
      <span className="txt">Thinking…</span>
    </div>
  );
}