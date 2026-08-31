from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import os
import re
import secrets
import sqlite3
from threading import Lock
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request, Response

from database import get_connection

SESSION_COOKIE = "evopay_session"
CSRF_COOKIE = "evopay_csrf"
SESSION_HOURS = max(1, int(os.getenv("EVOPAY_SESSION_HOURS", "12")))
COOKIE_SECURE = os.getenv("EVOPAY_ENV", "development").lower() == "production"
COOKIE_SAMESITE = "none" if COOKIE_SECURE else "lax"
PASSWORD_HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_attempts: dict[str, deque[float]] = defaultdict(deque)
_attempt_lock = Lock()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if len(normalized) > 254 or not EMAIL_PATTERN.fullmatch(normalized):
        raise HTTPException(422, "Enter a valid email address")
    return normalized


def validate_password(password: str) -> None:
    if len(password) < 12 or len(password) > 128:
        raise HTTPException(422, "Password must be between 12 and 128 characters")
    if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
        raise HTTPException(422, "Password must include at least one letter and one number")


def enforce_rate_limit(key: str, limit: int = 5, window_seconds: int = 60) -> None:
    import time
    current = time.monotonic()
    with _attempt_lock:
        bucket = _attempts[key]
        while bucket and current - bucket[0] >= window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(429, "Too many authentication attempts. Try again later.", headers={"Retry-After": str(window_seconds)})
        bucket.append(current)


def clear_rate_limits() -> None:
    with _attempt_lock:
        _attempts.clear()


def token_hash(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def public_user(row: sqlite3.Row | dict) -> dict[str, str]:
    return {"id": row["id"], "email": row["email"], "display_name": row["display_name"]}


def set_session_cookies(response: Response, session_token: str, csrf_token: str) -> None:
    max_age = SESSION_HOURS * 3600
    common = {"secure": COOKIE_SECURE, "samesite": COOKIE_SAMESITE, "path": "/", "max_age": max_age}
    response.set_cookie(SESSION_COOKIE, session_token, httponly=True, **common)
    response.set_cookie(CSRF_COOKIE, csrf_token, httponly=False, **common)


def clear_session_cookies(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)
    response.delete_cookie(CSRF_COOKIE, path="/", secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)


def create_session(connection: sqlite3.Connection, user_id: str, response: Response) -> None:
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(24)
    created_at = utc_now()
    expires_at = created_at + timedelta(hours=SESSION_HOURS)
    connection.execute(
        "INSERT INTO user_sessions (id, user_id, token_hash, csrf_hash, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid4()), user_id, token_hash(session_token), token_hash(csrf_token), created_at.isoformat(), expires_at.isoformat()),
    )
    set_session_cookies(response, session_token, csrf_token)


def current_user(request: Request) -> dict[str, str]:
    session_token = request.cookies.get(SESSION_COOKIE)
    if not session_token:
        raise HTTPException(401, "Authentication required")
    with get_connection() as connection:
        session = connection.execute(
            "SELECT s.id AS session_id, s.csrf_hash, s.expires_at, u.id, u.email, u.display_name "
            "FROM user_sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?",
            (token_hash(session_token),),
        ).fetchone()
        if not session:
            raise HTTPException(401, "Session is invalid or has ended")
        if datetime.fromisoformat(session["expires_at"]) <= utc_now():
            connection.execute("DELETE FROM user_sessions WHERE id = ?", (session["session_id"],))
            connection.commit()
            raise HTTPException(401, "Session has expired")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            csrf_cookie = request.cookies.get(CSRF_COOKIE)
            csrf_header = request.headers.get("X-CSRF-Token")
            if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header) or not secrets.compare_digest(token_hash(csrf_header), session["csrf_hash"]):
                raise HTTPException(403, "CSRF validation failed")
        return public_user(session)


AuthenticatedUser = Depends(current_user)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False
