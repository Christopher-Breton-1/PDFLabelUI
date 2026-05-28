from pydantic import BaseModel


class Box(BaseModel):
    page: int
    text: str
    bbox: tuple
    label: str
