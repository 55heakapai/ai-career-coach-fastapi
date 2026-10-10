const BASE = import.meta.env.VITE_API_URL || "/api";
const KEY = "waypoint_token";
let onUnauthorized = () => {};

export const setUnauthorizedHandler = (fn) => (onUnauthorized = fn);
export const getToken = () => localStorage.getItem(KEY);
export const setToken = (t) => (t ? localStorage.setItem(KEY, t) : localStorage.removeItem(KEY));

async function request(path, { method = "GET", body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body) headers["Content-Type"] = "application/json";
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: form ?? (body ? JSON.stringify(body) : undefined),
  });
  if (res.status === 401 && token) onUnauthorized();
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => d.msg).join(", ") : data.detail;
    throw new Error(detail || "Something went wrong. Try again.");
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  register: (body) => request("/auth/register", { method: "POST", body }),
  login: (body) => request("/auth/login", { method: "POST", body }),
  me: () => request("/auth/me"),
  saveProfile: (body) => request("/auth/profile", { method: "PUT", body }),
  chat: (body) => request("/chat", { method: "POST", body }),
  conversations: () => request("/chat/conversations"),
  conversation: (id) => request(`/chat/conversations/${id}`),
  deleteConversation: (id) => request(`/chat/conversations/${id}`, { method: "DELETE" }),
  analyzeResume: (form) => request("/resume/analyze", { method: "POST", form }),
  questions: (body) => request("/interview/questions", { method: "POST", body }),
  evaluate: (body) => request("/interview/evaluate", { method: "POST", body }),
};
