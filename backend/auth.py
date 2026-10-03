"""FastAPI dependencies that ENFORCE authentication (401) and role-based access (403)."""
from fastapi import Depends, Header, HTTPException
from backend.guard import role_for, authorized

def principal(authorization: str | None = Header(default=None)):
    token = authorization.split(" ", 1)[1].strip() if authorization and authorization.lower().startswith("bearer ") else None
    role = role_for(token)
    if role is None: raise HTTPException(status_code=401, detail="missing or invalid bearer token", headers={"WWW-Authenticate": "Bearer"})
    return {"role": role}

def require(action: str):
    def dep(p=Depends(principal)):
        if not authorized(p["role"], action): raise HTTPException(status_code=403, detail=f"role '{p['role']}' may not '{action}'")
        return p
    return dep
