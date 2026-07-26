from fastapi import Header, HTTPException, status

async def get_current_user(authorization: str = Header(...)) -> str:
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth scheme. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = parts[1]    
    if "valid" not in token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return 'user_123'