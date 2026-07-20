from fastapi import HTTPException


class BadRequest(HTTPException):
    def __init__(self, detail: str = ""):
        super().__init__(status_code=400, detail=detail or "Bad Request")


class Forbidden(HTTPException):
    def __init__(self, detail: str = ""):
        super().__init__(status_code=403, detail=detail or "Forbidden")


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "application error"):
        super().__init__(status_code=500, detail=detail)
