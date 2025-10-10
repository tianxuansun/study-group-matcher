from fastapi import HTTPException, status

def not_found(msg: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": {"code": "not_found", "message": msg}},
    )

def conflict(msg: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error": {"code": "conflict", "message": msg}},
    )
