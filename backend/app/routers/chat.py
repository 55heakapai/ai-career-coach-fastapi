from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import current_user
from app.db.models import Conversation, Message, User
from app.db.session import get_db
from app.schemas import ChatIn, ChatOut, ConversationOut, MessageOut
from app.services.llm import LLMError, get_llm
from app.services.prompts import coach_system_prompt

router = APIRouter(prefix="/chat", tags=["chat"])
HISTORY_LIMIT = 20  # only the latest turns are sent to the model, which bounds cost and latency


def _owned(db: Session, conversation_id: int, user: User) -> Conversation:
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "Conversation not found.")
    return conv


@router.post("", response_model=ChatOut)
def chat(body: ChatIn, user: User = Depends(current_user), db: Session = Depends(get_db), llm=Depends(get_llm)):
    if body.conversation_id:
        conv = _owned(db, body.conversation_id, user)
    else:
        conv = Conversation(user_id=user.id, title=body.message.strip()[:60])
        db.add(conv)
        db.flush()

    history = [{"role": m.role, "content": m.content} for m in conv.messages[-HISTORY_LIMIT:]]
    history.append({"role": "user", "content": body.message})
    try:
        reply = llm.chat(coach_system_prompt(user), history)
    except LLMError as exc:
        db.rollback()
        raise HTTPException(502, str(exc))

    db.add_all([
        Message(conversation_id=conv.id, role="user", content=body.message),
        Message(conversation_id=conv.id, role="assistant", content=reply),
    ])
    db.commit()
    return ChatOut(conversation_id=conv.id, reply=reply)


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    stmt = select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.id.desc())
    return db.scalars(stmt).all()


@router.get("/conversations/{conversation_id}", response_model=list[MessageOut])
def get_conversation(conversation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _owned(db, conversation_id, user).messages


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(_owned(db, conversation_id, user))
    db.commit()
