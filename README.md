# Waypoint: AI-powered career guidance platform

A career coaching app where students and early-career engineers can talk through their goals with a
conversational coach, get a resume analysed against a target role, and practise interview questions
with scored feedback.

**Stack:** React (Vite), Python, FastAPI, SQLAlchemy (SQLite or PostgreSQL), JWT auth, scikit-learn (NLP), Gemini (LLM)

## Features
- **Conversational coach**: multi-turn chat with saved sessions. The system prompt includes the user's profile
  (target role, level, skills) so advice is personalised.
- **Resume lab**: upload a PDF/TXT or paste text. An NLP step extracts skills, scores coverage against the role
  (or a pasted job description), measures TF-IDF similarity, and checks structure. The LLM then writes feedback and bullet rewrites.
- **Interview room**: generates role-specific questions, then scores each answer from 1 to 10 with strengths,
  improvements and an outline of a strong answer.
- **Accounts**: register/login with bcrypt-hashed passwords and JWT bearer tokens. Each user only sees their own conversations.

## Architecture
```
React (Vite) --/api--> FastAPI routers --> services/llm.py  --> Gemini API
                          |                services/nlp.py  (scikit-learn)
                          +--> SQLAlchemy --> SQLite / PostgreSQL
```
- `routers/` handle HTTP and validation; `services/` hold the LLM and NLP logic; `db/` holds models.
- The LLM sits behind a small interface (`chat`, `json`) with a mock implementation, so tests and offline demos need no API key.

## Design decisions
- **NLP before the LLM.** Skill coverage, TF-IDF similarity and structure checks are deterministic and cheap, and
  they ground the model's feedback in measurements instead of guesses.
- **Bounded history.** Only the last 20 messages go to the model, which limits cost and latency.
- **Structured output.** Resume and interview endpoints ask for JSON, parse it defensively, and clamp or default
  fields so a malformed reply cannot crash the API.
- **Prompt-injection hygiene.** Resumes and answers are labelled as untrusted data in the system prompts.
- **Sync endpoints.** FastAPI runs them in a thread pool, which suits the blocking HTTP call to the model.

## Run locally
```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY and a long random SECRET_KEY
uvicorn app.main:app --reload

# frontend (new terminal)
cd frontend
npm install
npm run dev                 # http://localhost:5173
```
Without a `GEMINI_API_KEY` the app runs in demo mode with canned responses. API docs: http://localhost:8000/docs.

Tests: `cd backend && pytest`

## API overview
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register, /api/auth/login | Create account / get JWT |
| GET, PUT | /api/auth/me, /api/auth/profile | Read / update profile |
| POST | /api/chat | Send a message (creates or continues a conversation) |
| GET, DELETE | /api/chat/conversations[/{id}] | List, read, delete sessions |
| POST | /api/resume/analyze | NLP signals + LLM feedback (multipart) |
| POST | /api/interview/questions | Generate questions |
| POST | /api/interview/evaluate | Score one answer |

## Limitations and next steps
- No rate limiting or refresh tokens yet; tables are created on startup instead of via Alembic migrations.
- Skill extraction uses a curated taxonomy; a spaCy NER or embedding model would generalise better.
- Chat replies are returned whole; streaming (SSE) would improve perceived speed.
- Scanned (image-only) PDFs are not supported.

