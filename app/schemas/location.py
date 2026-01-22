from pydantic import BaseModel, Field
from typing import Optional


class LocationBase(BaseModel):
    """Esquema base de ubicación"""
    city: str = Field(..., description="Ciudad del usuario")
    region: str = Field(..., description="Región/Estado/Provincia")
    country: str = Field(..., description="País")
    country_code: Optional[str] = Field(None, description="Código ISO del país")
    latitude: Optional[float] = Field(None, description="Latitud")
    longitude: Optional[float] = Field(None, description="Longitud")


class LocationRequest(BaseModel):
    """Request manual de ubicación (opcional)"""
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None


class LocationResponse(LocationBase):
    """Response de ubicación detectada"""
    ip: Optional[str] = Field(None, description="IP del usuario")
    timezone: Optional[str] = Field(None, description="Zona horaria")
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Santiago",
                "region": "Región Metropolitana",
                "country": "Chile",
                "country_code": "CL",
                "latitude": -33.4489,
                "longitude": -70.6693,
                "ip": "190.162.xxx.xxx",
                "timezone": "America/Santiago"
            }
        }