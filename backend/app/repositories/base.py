from typing import Generic, TypeVar, Type, Sequence, Any

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic base repository.
    """

    def __init__(self, db: Session, model: Type[T]) -> None:
        self.db = db
        self.model = model

    def get(self, id: Any) -> T | None:
        return self.db.query(self.model).get(id)

    def get_all(self) -> Sequence[T]:
        return self.db.query(self.model).all()

    def create(self, instance: T) -> T:
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: T) -> None:
        self.db.delete(instance)
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: T) -> None:
        self.db.refresh(instance)