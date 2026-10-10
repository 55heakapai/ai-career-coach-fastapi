from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import models  # noqa: F401  (registers tables on Base)
from app.db.session import Base, engine
from app.routers import auth, chat, interview, resume


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)  # fine for a demo; use Alembic migrations for real deployments
    yield


app = FastAPI(title="Waypoint API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, chat.router, resume.router, interview.router):
    app.include_router(r, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
