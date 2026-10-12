import hashlib
import secrets

from .models import UserSession


def create_session(db, user_id: int) -> str:
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    session = UserSession(
        user_id=user_id,
        token_hash=token_hash
    )

    db.add(session)
    db.commit()

    return token


def get_user_id_from_token(db, token: str):
    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == token_hash)
        .first()
    )

    if not session:
        return None

    return session.user_id


def delete_session(db, token: str):
    if not token:
        return

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == token_hash)
        .first()
    )

    if session:
        db.delete(session)
        db.commit()
