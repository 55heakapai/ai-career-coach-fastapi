import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(pattern=EMAIL, max_length=255)
    password: str = Field(min_length=8, max_length=72)  # bcrypt hashes at most 72 bytes


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileIn(BaseModel):
    target_role: str = Field(default="", max_length=120)
    experience_level: str = Field(default="student", max_length=40)
    skills: str = Field(default="", max_length=1000)


class UserOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: int | None = None


class ChatOut(BaseModel):
    conversation_id: int
    reply: str


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    created_at: dt.datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    content: str


class QuestionsIn(BaseModel):
    role: str = Field(min_length=2, max_length=120)
    level: str = Field(default="intern", max_length=40)
    count: int = Field(default=5, ge=1, le=10)
    focus: str = Field(default="", max_length=200)


class EvaluateIn(BaseModel):
    role: str = Field(min_length=2, max_length=120)
    question: str = Field(min_length=5, max_length=600)
    answer: str = Field(min_length=10, max_length=4000)
