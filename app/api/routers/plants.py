from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.plants import PlantCreate, PlantUpdate, Plant
from app.api.services import plants_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("/", response_model=Plant, status_code=status.HTTP_201_CREATED)
def create_plant_endpoint(plant: PlantCreate, db: Session = Depends(get_db)):
    try:
        return plants_service.create_plant(db, plant)
    except Exception as e:
        # Check for specific exceptions like duplicate key or invalid foreign key if possible
        # For now, a generic 400 is raised, but ideally we catch specifics in service
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Plant])
def list_plants_endpoint(db: Session = Depends(get_db)):
    return plants_service.get_plants(db)


@router.get("/{plant_id}", response_model=Plant)
def get_plant_endpoint(plant_id: str, db: Session = Depends(get_db)):
    db_plant = plants_service.get_plant(db, plant_id)
    if not db_plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return db_plant


@router.put("/{plant_id}", response_model=Plant)
def update_plant_endpoint(
    plant_id: str, plant: PlantUpdate, db: Session = Depends(get_db)
):
    db_plant = plants_service.update_plant(db, plant_id, plant)
    if not db_plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return db_plant


@router.delete("/{plant_id}", response_model=Plant)
def delete_plant_endpoint(plant_id: str, db: Session = Depends(get_db)):
    db_plant = plants_service.delete_plant(db, plant_id)
    if not db_plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return db_plant
