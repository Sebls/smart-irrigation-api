from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.plants import PlantModel
from app.api.schemas.plants import PlantCreate, PlantUpdate, Plant


def create_plant(db: Session, plant: PlantCreate) -> Plant:
    try:
        # Convert zone_id string to UUID if necessary, though Pydantic/SQLAlchemy might handle it.
        # Explicit conversion is safer.
        zone_uuid = uuid.UUID(plant.zone_id)
        db_plant = PlantModel(
            name=plant.name,
            zone_id=zone_uuid,
            image_url=plant.image_url,
            health=plant.health,
        )
        db.add(db_plant)
        db.commit()
        db.refresh(db_plant)
        return Plant.model_validate(db_plant)
    except ValueError:
        raise ValueError("Invalid UUID format for zone_id")
    except IntegrityError as e:
        db.rollback()
        # In a real app, parse 'e' to see if it's a FK violation or Unique violation
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_plants(db: Session) -> List[Plant]:
    db_plants = db.query(PlantModel).all()
    # Pydantic v2 validation from list
    return [Plant.model_validate(plant) for plant in db_plants]


def get_plant(db: Session, plant_id: str) -> Optional[Plant]:
    try:
        plant_uuid = uuid.UUID(plant_id)
    except ValueError:
        return None

    db_plant = db.query(PlantModel).filter(PlantModel.id == plant_uuid).first()
    if not db_plant:
        return None
    return Plant.model_validate(db_plant)


def update_plant(db: Session, plant_id: str, plant: PlantUpdate) -> Optional[Plant]:
    try:
        plant_uuid = uuid.UUID(plant_id)
    except ValueError:
        return None

    db_plant = db.query(PlantModel).filter(PlantModel.id == plant_uuid).first()
    if not db_plant:
        return None

    data = plant.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_plant, key, value)

    try:
        db.commit()
        db.refresh(db_plant)
        return Plant.model_validate(db_plant)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")


def delete_plant(db: Session, plant_id: str) -> Optional[Plant]:
    try:
        plant_uuid = uuid.UUID(plant_id)
    except ValueError:
        return None

    db_plant = db.query(PlantModel).filter(PlantModel.id == plant_uuid).first()
    if not db_plant:
        return None

    db.delete(db_plant)
    db.commit()
    return Plant.model_validate(db_plant)
