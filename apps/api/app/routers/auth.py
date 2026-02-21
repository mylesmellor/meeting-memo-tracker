import re
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.models.organisation import Organisation
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_OPTS = {
    "httponly": True,
    "samesite": "lax",
    "path": "/",
}


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    secure = settings.APP_ENV == "production"
    response.set_cookie("access_token", access_token, secure=secure, **COOKIE_OPTS)
    response.set_cookie("refresh_token", refresh_token, secure=secure, **COOKIE_OPTS)


def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


def slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug[:80]


@router.post("/register")
async def register(body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create org with unique slug
    base_slug = slugify(body.org_name)
    slug = base_slug
    suffix = 1
    while True:
        existing_org = await db.execute(select(Organisation).where(Organisation.slug == slug))
        if not existing_org.scalar_one_or_none():
            break
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    org = Organisation(id=uuid.uuid4(), name=body.org_name, slug=slug, created_at=datetime.utcnow())
    db.add(org)
    await db.flush()

    user = User(
        id=uuid.uuid4(),
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
        role=UserRole.org_admin,
        org_id=org.id,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    set_auth_cookies(response, access_token, refresh_token)
    return {"message": "Registered successfully", "user": UserOut.model_validate(user)}


@router.post("/login")
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    set_auth_cookies(response, access_token, refresh_token)
    return {"message": "Logged in", "user": UserOut.model_validate(user)}


@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    from jose import JWTError
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token({"sub": str(user.id)})
    secure = settings.APP_ENV == "production"
    response.set_cookie("access_token", access_token, secure=secure, **COOKIE_OPTS)
    return {"message": "Token refreshed"}


@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.get("/users/")
async def list_org_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.org_id == current_user.org_id)
        .order_by(User.name)
    )
    users = result.scalars().all()
    return [UserOut.model_validate(u) for u in users]
