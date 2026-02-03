from pydantic import BaseModel, ConfigDict

class PlantCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    zone_id: str
    image_url: str | None = None
    health: str

class PlantUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    image_url: str | None = None
    health: str | None = None

class Plant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    zone_id: str
    image_url: str | None = None
    health: str