import { useEffect, useState } from "react";
import { api, getToken, setToken, setUnauthorizedHandler } from "./api";
import Auth from "./pages/Auth";
import Coach from "./pages/Coach";
import Resume from "./pages/Resume";
import Interview from "./pages/Interview";
import Profile from "./pages/Profile";

const VIEWS = [
  ["coach", "Coach"],
  ["resume", "Resume lab"],
  ["interview", "Interview room"],
  ["profile", "Profile"],
];

export default function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(!getToken());
  const [view, setView] = useState("coach");

  const signOut = () => {
    setToken(null);
    setUser(null);
  };
  const loadUser = () =>
    api.me().then(setUser).catch(signOut).finally(() => setReady(true));

  useEffect(() => {
    setUnauthorizedHandler(signOut);
    if (getToken()) loadUser();
  }, []);

  if (!ready) return <p className="boot">Loading</p>;
  if (!user) return <Auth onAuthed={loadUser} />;

  return (
    <div className="shell">
      <nav className="rail" aria-label="Main">
        <div className="brand">Waypoint</div>
        <ul>
          {VIEWS.map(([id, label]) => (
            <li key={id}>
              <button className={view === id ? "on" : ""} onClick={() => setView(id)}>
                {label}
              </button>
            </li>
          ))}
        </ul>
        <div className="who">
          <span>{user.name}</span>
          <button onClick={signOut}>Sign out</button>
        </div>
      </nav>
      <main className="stage">
        {view === "coach" && <Coach user={user} />}
        {view === "resume" && <Resume user={user} />}
        {view === "interview" && <Interview user={user} />}
        {view === "profile" && <Profile user={user} onSaved={setUser} />}
      </main>
    </div>
  );
}
