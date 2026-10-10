import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader

from app.core.security import current_user
from app.db.models import User
from app.services import nlp
from app.services.llm import LLMError, get_llm
from app.services.prompts import RESUME_SYSTEM

router = APIRouter(prefix="/resume", tags=["resume"])
MAX_BYTES = 2 * 1024 * 1024


def read_resume(file: UploadFile | None, text: str) -> str:
    if file and file.filename:
        data = file.file.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise HTTPException(413, "That file is larger than 2 MB.")
        name = file.filename.lower()
        if name.endswith(".pdf"):
            try:
                text = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
            except Exception:
                raise HTTPException(400, "Could not read this PDF. Paste the text instead.")
        elif name.endswith(".txt"):
            text = data.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(400, "Upload a PDF or TXT file, or paste your resume text.")
    text = (text or "").strip()
    if len(text) < 100:
        raise HTTPException(400, "Resume text is too short to analyse. Paste at least a few lines.")
    return text[:12000]


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


@router.post("/analyze")
def analyze_resume(
    target_role: str = Form(..., min_length=2, max_length=120),
    job_description: str = Form("", max_length=8000),
    resume_text: str = Form("", max_length=20000),
    file: UploadFile | None = File(None),
    user: User = Depends(current_user),
    llm=Depends(get_llm),
):
    resume = read_resume(file, resume_text)
    signals = nlp.analyze(resume, target_role, job_description)

    prompt = (
        f"Target role: {target_role}\n"
        f"Job description (may be empty): {job_description[:4000]}\n\n"
        f"NLP measurements: {signals}\n\n"
        f"Resume text:\n{resume[:6000]}"
    )
    try:
        raw = llm.json("resume", RESUME_SYSTEM, prompt)
    except LLMError as exc:
        raise HTTPException(502, str(exc))

    feedback = {
        "summary": str(raw.get("summary", "")),
        "strengths": _as_list(raw.get("strengths")),
        "improvements": _as_list(raw.get("improvements")),
        "rewritten_bullets": _as_list(raw.get("rewritten_bullets")),
    }
    return {"nlp": signals, "feedback": feedback}
