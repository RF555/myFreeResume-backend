from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from app.config import settings
from app.database import get_db
from app.exceptions import UnauthorizedError
from app.limiter import limiter
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.services.user_service import create_user, find_or_create_oauth_user, get_user_by_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

oauth.register(
    name="linkedin",
    client_id=settings.linkedin_client_id,
    client_secret=settings.linkedin_client_secret,
    authorize_url="https://www.linkedin.com/oauth/v2/authorization",
    access_token_url="https://www.linkedin.com/oauth/v2/accessToken",
    client_kwargs={"scope": "openid profile email"},
)


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/api/auth",
    )


async def _store_refresh_token(db, user_id: str, token: str) -> None:
    await db.refresh_tokens.insert_one(
        {
            "user_id": user_id,
            "token_hash": hash_token(token),
            "expires_at": datetime.now(timezone.utc)
            + timedelta(days=settings.jwt_refresh_token_expire_days),
            "created_at": datetime.now(timezone.utc),
        }
    )


@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, response: Response):
    db = get_db()
    user = await create_user(
        db,
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
    )
    user_id = str(user["_id"])
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    await _store_refresh_token(db, user_id, refresh_token)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, response: Response):
    db = get_db()
    user = await get_user_by_email(db, data.email)
    if not user or not user.get("password_hash"):
        raise UnauthorizedError()
    if not verify_password(data.password, user["password_hash"]):
        raise UnauthorizedError()

    user_id = str(user["_id"])
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    await _store_refresh_token(db, user_id, refresh_token)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(request: Request, response: Response):
    db = get_db()
    old_token = request.cookies.get("refresh_token")
    if old_token:
        try:
            payload = decode_refresh_token(old_token)
            user_id = payload["sub"]
            await db.refresh_tokens.delete_many({"user_id": user_id})
        except Exception:
            pass
    response.delete_cookie(
        key="refresh_token", path="/api/auth", samesite="none", secure=True
    )
    return {"message": "Logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response):
    db = get_db()
    old_token = request.cookies.get("refresh_token")
    if not old_token:
        raise UnauthorizedError("No refresh token")

    try:
        payload = decode_refresh_token(old_token)
        user_id = payload["sub"]
    except Exception:
        raise UnauthorizedError("Invalid refresh token")

    token_hash = hash_token(old_token)
    stored = await db.refresh_tokens.find_one_and_delete(
        {"user_id": user_id, "token_hash": token_hash}
    )
    if not stored:
        await db.refresh_tokens.delete_many({"user_id": user_id})
        raise UnauthorizedError("Refresh token reuse detected")

    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)
    await _store_refresh_token(db, user_id, new_refresh_token)
    _set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(access_token=access_token)


@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    client = getattr(oauth, provider, None)
    if not client:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    redirect_uri = f"{request.base_url}api/auth/oauth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, response: Response):
    client = getattr(oauth, provider, None)
    if not client:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    token = await client.authorize_access_token(request)

    if provider == "google":
        user_info = token.get("userinfo", {})
        email = user_info.get("email")
        name = user_info.get("name", "")
        provider_id = user_info.get("sub")
    elif provider == "github":
        resp = await client.get("user", token=token)
        user_info = resp.json()
        email = user_info.get("email")
        if not email:
            emails_resp = await client.get("user/emails", token=token)
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else None
        name = user_info.get("name", user_info.get("login", ""))
        provider_id = str(user_info.get("id"))
    elif provider == "linkedin":
        user_info = token.get("userinfo", {})
        email = user_info.get("email")
        name = user_info.get("name", "")
        provider_id = user_info.get("sub")
    else:
        raise HTTPException(status_code=400, detail="Unknown provider")

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from provider")

    db = get_db()
    user = await find_or_create_oauth_user(db, email, name, provider, provider_id)

    user_id = str(user["_id"])
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    await _store_refresh_token(db, user_id, refresh_token)

    params = urlencode({"access_token": access_token})
    redirect = RedirectResponse(url=f"{settings.frontend_url}/auth/callback?{params}")
    redirect.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=True, samesite="none",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/api/auth",
    )
    return redirect
