from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_db
from app.exceptions import UnauthorizedError
from app.services.auth_service import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token payload")
    except UnauthorizedError:
        raise
    except Exception:
        raise UnauthorizedError("Invalid or expired token")

    from bson import ObjectId

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise UnauthorizedError("User not found")

    user["id"] = str(user["_id"])
    return user
