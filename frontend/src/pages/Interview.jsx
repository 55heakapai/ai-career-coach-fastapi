import { useState } from "react";
import { api } from "../api";

export default function Interview({ user }) {
  const [setup, setSetup] = useState({ role: user.target_role || "", level: user.experience_level || "intern", count: 5, focus: "" });
  const [qs, setQs] = useState([]);
  const [i, setI] = useState(0);
  const [answer, setAnswer] = useState("");
  const [hint, setHint] = useState(false);
  const [review, setReview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const set = (k) => (e) => setSetup({ ...setup, [k]: e.target.value });

  async function start(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const out = await api.questions({ ...setup, count: Number(setup.count) });
      if (!out.questions.length) throw new Error("No questions came back. Try again.");
      setQs(out.questions);
      setI(0);
      reset();
    } catch (ex) {
      setError(ex.message);
    } finally {
      setBusy(false);
    }
  }
  const reset = () => { setAnswer(""); setReview(null); setHint(false); setError(""); };

  async function grade(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      setReview(await api.evaluate({ role: setup.role, question: qs[i].question, answer }));
    } catch (ex) {
      setError(ex.message);
    } finally {
      setBusy(false);
    }
  }

  if (!qs.length) {
    return (
      <form className="room-setup" onSubmit={start}>
        <h2>Interview room</h2>
        <p className="hint">Pick a role and practise one question at a time. You get a score and specific feedback on each answer.</p>
        <label>Role<input value={setup.role} onChange={set("role")} required minLength={2} /></label>
        <label>Level
          <select value={setup.level} onChange={set("level")}>
            <option value="intern">Intern</option><option value="junior">Junior</option><option value="mid-level">Mid-level</option>
          </select>
        </label>
        <label>Number of questions<input type="number" min="1" max="10" value={setup.count} onChange={set("count")} /></label>
        <label>Focus <small>optional, for example databases or project walkthroughs</small><input value={setup.focus} onChange={set("focus")} /></label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="primary" disabled={busy}>{busy ? "Preparing questions" : "Start practice"}</button>
      </form>
    );
  }

  const q = qs[i];
  const last = i === qs.length - 1;
  return (
    <div className="room">
      <p className="meta">Question {i + 1} of {qs.length}, {q.type}</p>
      <h2 className="question">{q.question}</h2>
      {q.hint && (hint ? <p className="hint">{q.hint}</p> : <button className="link" onClick={() => setHint(true)}>Show a hint</button>)}
      <form onSubmit={grade}>
        <textarea rows={7} value={answer} onChange={(e) => setAnswer(e.target.value)} disabled={!!review}
          placeholder="Answer the way you would out loud. Aim for two or three minutes." required minLength={10} />
        {error && <p className="error" role="alert">{error}</p>}
        {!review && <button className="primary" disabled={busy || answer.trim().length < 10}>{busy ? "Scoring" : "Get feedback"}</button>}
      </form>

      {review && (
        <div className="review">
          <p className="verdict">You scored <mark>{review.score} out of 10</mark> on this answer.</p>
          <h3>What worked</h3><ul>{review.strengths.map((s, k) => <li key={k}>{s}</li>)}</ul>
          <h3>To improve</h3><ul>{review.improvements.map((s, k) => <li key={k}>{s}</li>)}</ul>
          <h3>A strong answer would</h3><ul>{review.model_answer_outline.map((s, k) => <li key={k}>{s}</li>)}</ul>
          <div className="row">
            {!last && <button className="primary" onClick={() => { setI(i + 1); reset(); }}>Next question</button>}
            <button className="link" onClick={() => { setQs([]); reset(); }}>{last ? "Finish and start over" : "End practice"}</button>
          </div>
        </div>
      )}
    </div>
  );
}
