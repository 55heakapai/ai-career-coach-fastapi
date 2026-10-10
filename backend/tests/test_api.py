from app.services import nlp

RESUME = """Summary
Backend developer who builds APIs with Python, FastAPI and PostgreSQL.
Experience
Built a REST API serving 2000 requests per day, deployed with Docker on AWS.
Projects
Hotel booking platform using Java, Spring Boot and SQL with JUnit tests.
Skills
Python, Java, Docker, Git, Data Structures"""


def test_register_login_and_me(client):
    body = {"name": "Asha", "email": "Asha@Example.com", "password": "correct-horse"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    assert client.post("/api/auth/register", json=body).status_code == 409
    token = client.post("/api/auth/login", json={"email": "asha@example.com", "password": "correct-horse"}).json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["name"] == "Asha"
    assert client.post("/api/auth/login", json={"email": "asha@example.com", "password": "wrong-password"}).status_code == 401


def test_endpoints_require_auth(client):
    assert client.get("/api/chat/conversations").status_code == 401
    assert client.post("/api/interview/questions", json={"role": "Backend"}).status_code == 401


def test_chat_keeps_history_per_user(client, auth):
    first = client.post("/api/chat", json={"message": "How do I become a backend engineer?"}, headers=auth).json()
    cid = first["conversation_id"]
    client.post("/api/chat", json={"message": "What should I build first?", "conversation_id": cid}, headers=auth)
    msgs = client.get(f"/api/chat/conversations/{cid}", headers=auth).json()
    assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"]

    other = client.post("/api/auth/register", json={"name": "B", "email": "b@example.com", "password": "another-pass1"}).json()
    other_auth = {"Authorization": f"Bearer {other['access_token']}"}
    assert client.get(f"/api/chat/conversations/{cid}", headers=other_auth).status_code == 404


def test_resume_analysis_and_validation(client, auth):
    res = client.post("/api/resume/analyze", data={"target_role": "Backend Developer", "resume_text": RESUME}, headers=auth)
    assert res.status_code == 200
    data = res.json()
    assert "Python" in data["nlp"]["skills_found"] and "SQL" in data["nlp"]["skills_matched"]
    assert data["feedback"]["strengths"]
    short = client.post("/api/resume/analyze", data={"target_role": "Backend", "resume_text": "too short"}, headers=auth)
    assert short.status_code == 400


def test_interview_flow(client, auth):
    qs = client.post("/api/interview/questions", json={"role": "Backend Developer", "count": 2}, headers=auth).json()["questions"]
    assert len(qs) == 2
    ev = client.post("/api/interview/evaluate", json={"role": "Backend", "question": qs[0]["question"], "answer": "I built a booking API and handled double bookings with a transaction."}, headers=auth)
    assert ev.status_code == 200 and 1 <= ev.json()["score"] <= 10


def test_nlp_skill_extraction_edge_cases():
    skills = nlp.extract_skills("Experienced in JavaScript, Node.js, C++ and PostgreSQL.")
    assert {"JavaScript", "Node.js", "C++", "PostgreSQL"} <= skills
    assert "Java" not in skills  # "JavaScript" must not count as Java
    with_jd = nlp.analyze(RESUME, "Backend", "We need Python, Docker, Kubernetes and PostgreSQL experience.")
    assert "Kubernetes" in with_jd["skills_missing"] and with_jd["similarity"] is not None
