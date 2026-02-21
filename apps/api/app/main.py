from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.routers import auth, meetings, actions, tags, teams, demo


def get_user_id_or_ip(request: Request) -> str:
    user = getattr(request.state, "user", None)
    if user:
        return str(user.id)
    return get_remote_address(request)


limiter = Limiter(key_func=get_user_id_or_ip)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Meeting Memo Tracker API",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(meetings.router, prefix="/api/v1")
app.include_router(actions.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
