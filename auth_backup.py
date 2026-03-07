# ==========================================================
# 🔐 JWT AUTHENTICATION — Signup / Login / Token Logic
# ==========================================================

import json
import os
import hashlib
import hmac
import base64
import time

# ==========================================================
# CONFIG
# ==========================================================

JWT_SECRET = "aura-secret-key-change-in-production"
JWT_EXPIRY_HOURS = 24
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


# ==========================================================
# USER STORAGE (simple JSON file)
# ==========================================================


def _load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_users(users: dict):
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
# SIGNUP / LOGIN
# ==========================================================


def signup_user(username: str, password: str) -> tuple[bool, str]:
    users = _load_users()
    if username in users:
        return False, "Username already exists"

    users[username] = {"password": hash_password(password)}
    _save_users(users)
    return True, "User created"


def login_user(username: str, password: str) -> tuple[bool, str]:
    users = _load_users()
    if username not in users:
        return False, "User not found"

    if not verify_password(password, users[username]["password"]):
        return False, "Invalid password"

    token = create_access_token(username)
    return True, token
