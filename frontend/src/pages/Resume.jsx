import { useState } from "react";
import { api } from "../api";

export default function Resume({ user }) {
  const [role, setRole] = useState(user.target_role || "");
  const [jd, setJd] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const form = new FormData();
    form.append("target_role", role);
    form.append("job_description", jd);
    form.append("resume_text", text);
    if (file) form.append("file", file);
    try {
      setResult(await api.analyzeResume(form));
    } catch (ex) {
      setError(ex.message);
    } finally {
      setBusy(false);
    }
  }

  const n = result?.nlp;
  const f = result?.feedback;

  return (
    <div className="lab">
      <form className="lab-form" onSubmit={submit}>
        <h2>Resume lab</h2>
        <label>Role you are aiming for<input value={role} onChange={(e) => setRole(e.target.value)} required minLength={2} placeholder="Backend developer intern" /></label>
        <label>Job description <small>optional, but it sharpens the match</small>
          <textarea rows={5} value={jd} onChange={(e) => setJd(e.target.value)} />
        </label>
        <label>Upload your resume <small>PDF or TXT, up to 2 MB</small>
          <input type="file" accept=".pdf,.txt" onChange={(e) => setFile(e.target.files[0] || null)} />
        </label>
        <label>Or paste it here
          <textarea rows={8} value={text} onChange={(e) => setText(e.target.value)} />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="primary" disabled={busy}>{busy ? "Reading your resume" : "Analyse resume"}</button>
      </form>

      <div className="lab-out">
        {!result && <p className="hint">Your results appear here: how well your skills fit the role, what is missing, and rewrites for weak bullets.</p>}
        {result && (
          <>
            <p className="verdict">
              Your resume covers <mark>{n.match_score}%</mark> of what {role || "this role"} usually asks for.
            </p>
            <p className="reply-text">{f.summary}</p>

            <h3>Skills the role expects</h3>
            <p className="skills">
              {n.skills_matched.map((s) => <mark key={s}>{s}</mark>)}
              {n.skills_missing.map((s) => <span key={s} className="gap" title="Not found in your resume">{s}</span>)}
              {!n.skills_matched.length && !n.skills_missing.length && "No skills detected."}
            </p>
            <p className="meta">
              Sections found: {n.sections_present.join(", ") || "none"}. {n.quantified_lines} of {n.total_lines} lines include numbers.
              {n.similarity !== null && ` Text similarity to the job description: ${Math.round(n.similarity * 100)}%.`}
            </p>

            <h3>What is working</h3>
            <ul>{f.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
            <h3>What to fix</h3>
            <ul>{f.improvements.map((s, i) => <li key={i}>{s}</li>)}</ul>

            {f.rewritten_bullets.length > 0 && (
              <>
                <h3>Bullet rewrites</h3>
                {f.rewritten_bullets.map((b, i) => (
                  <div className="rewrite" key={i}>
                    <p className="before">{b.original}</p>
                    <p className="after">{b.improved}</p>
                  </div>
                ))}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
