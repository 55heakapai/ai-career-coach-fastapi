from fastapi import APIRouter, Depends, HTTPException

from app.core.security import current_user
from app.db.models import User
from app.schemas import EvaluateIn, QuestionsIn
from app.services.llm import LLMError, get_llm
from app.services.prompts import EVALUATE_SYSTEM, QUESTIONS_SYSTEM

router = APIRouter(prefix="/interview", tags=["interview"])


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


@router.post("/questions")
def questions(body: QuestionsIn, user: User = Depends(current_user), llm=Depends(get_llm)):
    prompt = (
        f"Role: {body.role}\nLevel: {body.level}\nNumber of questions: {body.count}\n"
        f"Focus (optional): {body.focus or 'general'}"
    )
    try:
        raw = llm.json("questions", QUESTIONS_SYSTEM, prompt)
    except LLMError as exc:
        raise HTTPException(502, str(exc))
    items = [q for q in _as_list(raw.get("questions")) if isinstance(q, dict) and q.get("question")]
    return {"questions": items[: body.count]}


@router.post("/evaluate")
def evaluate(body: EvaluateIn, user: User = Depends(current_user), llm=Depends(get_llm)):
    prompt = f"Role: {body.role}\nQuestion: {body.question}\n\nCandidate answer:\n{body.answer}"
    try:
        raw = llm.json("evaluate", EVALUATE_SYSTEM, prompt)
    except LLMError as exc:
        raise HTTPException(502, str(exc))
    try:
        score = max(1, min(10, int(raw.get("score", 5))))
    except (TypeError, ValueError):
        score = 5
    return {
        "score": score,
        "strengths": _as_list(raw.get("strengths")),
        "improvements": _as_list(raw.get("improvements")),
        "model_answer_outline": _as_list(raw.get("model_answer_outline")),
    }
