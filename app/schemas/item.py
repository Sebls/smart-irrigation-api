from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str


class ItemCreate(ItemBase):
    pass


class ItemOut(ItemBase):
    id: int

