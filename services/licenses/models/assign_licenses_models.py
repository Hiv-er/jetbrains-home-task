from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    description: str
