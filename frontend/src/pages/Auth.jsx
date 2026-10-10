import { useState } from "react";
import { api, setToken } from "../api";

export default function Auth({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      const out = mode === "login" ? await api.login({ email: f.email, password: f.password }) : await api.register(f);
      setToken(out.access_token);
      onAuthed();
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth">
      <section className="auth-pitch">
        <h1>Know your next step before you take it.</h1>
        <p>
          Talk through your goals with a coach, get your resume read against the role you want, and
          practise the questions you will actually be asked.
        </p>
      </section>
      <form className="auth-form" onSubmit={submit}>
        <h2>{mode === "login" ? "Sign in" : "Create your account"}</h2>
        {mode === "register" && (
          <label>Name<input value={f.name} onChange={set("name")} required autoComplete="name" /></label>
        )}
        <label>Email<input type="email" value={f.email} onChange={set("email")} required autoComplete="email" /></label>
        <label>
          Password
          <input type="password" value={f.password} onChange={set("password")} required minLength={mode === "register" ? 8 : 1}
            autoComplete={mode === "login" ? "current-password" : "new-password"} />
        </label>
        {mode === "register" && <small>At least 8 characters.</small>}
        {err && <p className="error" role="alert">{err}</p>}
        <button className="primary" disabled={busy}>{busy ? "One moment" : mode === "login" ? "Sign in" : "Create account"}</button>
        <button type="button" className="link" onClick={() => { setMode(mode === "login" ? "register" : "login"); setErr(""); }}>
          {mode === "login" ? "New here? Create an account" : "Have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}
