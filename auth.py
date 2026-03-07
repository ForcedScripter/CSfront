# ==========================================================
# 🔐 JWT AUTHENTICATION — Supabase PostgreSQL Storage
# ==========================================================

import os
import hashlib
import hmac
import base64
import time
import json

from supabase import create_client, Client

# ==========================================================
# CONFIG
# ==========================================================

JWT_SECRET = os.getenv("JWT_SECRET", "aura-secret-key-change-in-production")
JWT_EXPIRY_HOURS = 24

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client (lazy — only when env vars are set)
_supabase: Client | None = None


def _get_supabase() -> Client | None:
    global _supabase
    if _supabase is not None:
        return _supabase
    if SUPABASE_URL and SUPABASE_KEY:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase
    return None


# ==========================================================
# FALLBACK — JSON file storage (when Supabase not configured)
# ==========================================================

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _load_users_json() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_users_json(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ==========================================================
# PASSWORD HASHING
# ==========================================================


def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(":")
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return hmac.compare_digest(check.hex(), h)


# ==========================================================
# JWT TOKEN (minimal, no external deps)
# ==========================================================


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def create_access_token(username: str) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": username,
                "exp": int(time.time()) + JWT_EXPIRY_HOURS * 3600,
            }
        ).encode()
    )
    signature = hmac.new(
        JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{header}.{payload}.{sig_b64}"


def decode_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header, payload, sig = parts

        expected_sig = hmac.new(
            JWT_SECRET.encode(),
            f"{header}.{payload}".encode(),
            hashlib.sha256,
        ).digest()
        actual_sig = _b64url_decode(sig)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        data = json.loads(_b64url_decode(payload))

        if data.get("exp", 0) < time.time():
            return None

        return data
    except Exception:
        return None


# ==========================================================
# SIGNUP / LOGIN — Supabase or JSON fallback
# ==========================================================


def signup_user(username: str, password: str) -> tuple[bool, str]:
    sb = _get_supabase()

    if sb:
        # ── Supabase path ──
        try:
            existing = sb.table("users").select("id").eq("username", username).execute()
            if existing.data:
                return False, "Username already exists"

            password_hash = hash_password(password)
            sb.table("users").insert(
                {"username": username, "password_hash": password_hash}
            ).execute()
            print(f"✅ User '{username}' created in Supabase")
            return True, "User created"
        except Exception as e:
            print(f"❌ Supabase signup error: {e}")
            return False, f"Database error: {str(e)}"
    else:
        # ── JSON fallback ──
        users = _load_users_json()
        if username in users:
            return False, "Username already exists"

        users[username] = {"password": hash_password(password)}
        _save_users_json(users)
        print(f"✅ User '{username}' created in users.json (fallback)")
        return True, "User created"


def login_user(username: str, password: str) -> tuple[bool, str]:
    sb = _get_supabase()

    if sb:
        # ── Supabase path ──
        try:
            result = sb.table("users").select("password_hash").eq("username", username).execute()
            if not result.data:
                return False, "User not found"

            stored_hash = result.data[0]["password_hash"]
            if not verify_password(password, stored_hash):
                return False, "Invalid password"

            token = create_access_token(username)
            return True, token
        except Exception as e:
            print(f"❌ Supabase login error: {e}")
            return False, f"Database error: {str(e)}"
    else:
        # ── JSON fallback ──
        users = _load_users_json()
        if username not in users:
            return False, "User not found"

        if not verify_password(password, users[username]["password"]):
            return False, "Invalid password"

        token = create_access_token(username)
        return True, token
