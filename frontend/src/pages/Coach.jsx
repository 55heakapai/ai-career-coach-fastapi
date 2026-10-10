import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../api";

const STARTERS = [
  "Map a path from my current skills to the role I want",
  "What should I build this month to stand out?",
  "Help me explain my projects in an interview",
];

export default function Coach({ user }) {
  const [convs, setConvs] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  const refresh = () => api.conversations().then(setConvs).catch(() => {});
  useEffect(() => { refresh(); }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, busy]);

  async function open(id) {
    setError("");
    setActiveId(id);
    setMessages(await api.conversation(id).catch(() => []));
  }
  const fresh = () => { setActiveId(null); setMessages([]); setError(""); };

  async function remove(id) {
    await api.deleteConversation(id);
    if (id === activeId) fresh();
    refresh();
  }

  async function send(text) {
    const message = (text ?? input).trim();
    if (!message || busy) return;
    setInput("");
    setError("");
    setMessages((m) => [...m, { role: "user", content: message }]);
    setBusy(true);
    try {
      const out = await api.chat({ message, conversation_id: activeId });
      setActiveId(out.conversation_id);
      setMessages((m) => [...m, { role: "assistant", content: out.reply }]);
      refresh();
    } catch (ex) {
      setError(ex.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="coach">
      <aside className="sessions" aria-label="Past sessions">
        <button className="primary" onClick={fresh}>New session</button>
        <ul>
          {convs.map((c) => (
            <li key={c.id} className={c.id === activeId ? "on" : ""}>
              <button onClick={() => open(c.id)}>{c.title}</button>
              <button className="x" aria-label={`Delete ${c.title}`} onClick={() => remove(c.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="talk">
        <div className="transcript">
          {messages.length === 0 && (
            <div className="empty">
              <h2>{user.target_role ? `Working toward ${user.target_role}` : "What are you working toward?"}</h2>
              {!user.target_role && <p>Set a target role in Profile and the coach will tailor every answer to it.</p>}
              <ul>
                {STARTERS.map((s) => (
                  <li key={s}><button onClick={() => send(s)}>{s}</button></li>
                ))}
              </ul>
            </div>
          )}
          {messages.map((m, i) =>
            m.role === "user" ? (
              <p key={i} className="said"><span>{m.content}</span></p>
            ) : (
              <div key={i} className="reply"><ReactMarkdown>{m.content}</ReactMarkdown></div>
            )
          )}
          {busy && <p className="thinking">Coach is writing</p>}
          {error && <p className="error" role="alert">{error}</p>}
          <div ref={endRef} />
        </div>
        <form className="composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
          <textarea
            value={input}
            rows={2}
            placeholder="Ask about skills, projects, resumes, or interviews"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
          />
          <button className="primary" disabled={busy || !input.trim()}>Send</button>
        </form>
      </section>
    </div>
  );
}
