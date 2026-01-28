from fastapi import APIRouter, Depends, status

from app.schemas.item import ItemCreate, ItemOut
from app.services.item_service import ItemRepository, get_item_repo

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemOut])
def list_items(repo: ItemRepository = Depends(get_item_repo)) -> list[ItemOut]:
    return [ItemOut(id=i.id, name=i.name) for i in repo.list_items()]


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, repo: ItemRepository = Depends(get_item_repo)) -> ItemOut:
    item = repo.create_item(name=payload.name)
    return ItemOut(id=item.id, name=item.name)
