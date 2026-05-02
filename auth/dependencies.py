from fastapi import HTTPException, Request

PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/login",
    "/signup",
}


def require_authenticated_user(request: Request):
    if not request.user or not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")
    return request.user
