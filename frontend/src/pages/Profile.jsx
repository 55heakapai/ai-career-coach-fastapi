import { useState } from "react";
import { api } from "../api";

export default function Profile({ user, onSaved }) {
  const [f, setF] = useState({ target_role: user.target_role, experience_level: user.experience_level, skills: user.skills });
  const [status, setStatus] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function save(e) {
    e.preventDefault();
    setStatus("");
    try {
      onSaved(await api.saveProfile(f));
      setStatus("Profile saved. The coach now uses it in every answer.");
    } catch (ex) {
      setStatus(ex.message);
    }
  }

  return (
    <form className="room-setup" onSubmit={save}>
      <h2>Your profile</h2>
      <p className="hint">The coach reads this before answering, so the advice fits you.</p>
      <label>Target role<input value={f.target_role} onChange={set("target_role")} placeholder="Backend developer intern" /></label>
      <label>Experience level
        <select value={f.experience_level} onChange={set("experience_level")}>
          <option value="student">Student</option><option value="intern">Intern</option><option value="junior">Junior</option><option value="mid-level">Mid-level</option>
        </select>
      </label>
      <label>Skills you have <small>separate with commas</small><textarea rows={3} value={f.skills} onChange={set("skills")} /></label>
      <button className="primary">Save profile</button>
      {status && <p className="meta" role="status">{status}</p>}
    </form>
  );
}
