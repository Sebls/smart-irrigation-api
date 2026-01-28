from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class Item:
    id: int
    name: str


class ItemRepository:
    """In-memory repository used for the sample endpoints and tests."""

    def __init__(self, initial: list[Item] | None = None) -> None:
        self._lock = Lock()
        self._items: list[Item] = list(initial or [])
        self._next_id = (max((i.id for i in self._items), default=0) + 1) if self._items else 1

    def list_items(self) -> list[Item]:
        with self._lock:
            return list(self._items)

    def create_item(self, *, name: str) -> Item:
        with self._lock:
            item = Item(id=self._next_id, name=name)
            self._next_id += 1
            self._items.append(item)
            return item


_default_repo = ItemRepository()


def get_item_repo() -> ItemRepository:
    """FastAPI dependency for injecting the item repository."""

    return _default_repo

