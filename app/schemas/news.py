from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class NewsCategory(str, Enum):
    """Categorías de noticias"""
    POLITICS = "política"
    ECONOMY = "economía"
    SPORTS = "deportes"
    TECHNOLOGY = "tecnología"
    ENTERTAINMENT = "entretenimiento"
    HEALTH = "salud"
    EDUCATION = "educación"
    SECURITY = "seguridad"
    ENVIRONMENT = "medio ambiente"
    LOCAL = "local"
    OTHER = "otros"


class NewsItem(BaseModel):
    """Esquema de una noticia individual"""
    id: int = Field(..., description="ID único de la noticia")
    title: str = Field(..., description="Título de la noticia")
    summary: str = Field(..., description="Resumen de la noticia")
    category: NewsCategory = Field(..., description="Categoría de la noticia")
    relevance_score: int = Field(
        ..., 
        ge=1, 
        le=10, 
        description="Puntuación de relevancia (1-10)"
    )
    location_context: str = Field(
        ..., 
        description="Contexto de por qué es relevante para la ubicación"
    )
    estimated_date: Optional[str] = Field(
        None, 
        description="Fecha estimada del evento/noticia"
    )
    keywords: List[str] = Field(
        default_factory=list, 
        description="Palabras clave relacionadas"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Nueva línea de metro conectará comunas del sector oriente",
                "summary": "El proyecto de extensión del metro...",
                "category": "local",
                "relevance_score": 9,
                "location_context": "Afecta directamente a Santiago",
                "estimated_date": "2024-01",
                "keywords": ["metro", "transporte", "infraestructura"]
            }
        }


class NewsRequest(BaseModel):
    """Request para obtener noticias"""
    city: Optional[str] = Field(None, description="Ciudad (opcional, se detecta automáticamente)")
    region: Optional[str] = Field(None, description="Región (opcional)")
    country: Optional[str] = Field(None, description="País (opcional)")
    categories: Optional[List[NewsCategory]] = Field(
        None, 
        description="Filtrar por categorías específicas"
    )
    limit: int = Field(
        default=10, 
        ge=1, 
        le=20, 
        description="Número máximo de noticias"
    )
    language: str = Field(
        default="es", 
        description="Idioma de las noticias"
    )


class NewsResponse(BaseModel):
    """Response con las noticias"""
    success: bool = Field(..., description="Si la operación fue exitosa")
    location: str = Field(..., description="Ubicación usada para la búsqueda")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Fecha de generación"
    )
    total_news: int = Field(..., description="Total de noticias encontradas")
    news: List[NewsItem] = Field(..., description="Lista de noticias")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "location": "Santiago, Región Metropolitana, Chile",
                "generated_at": "2024-01-22T10:30:00Z",
                "total_news": 5,
                "news": []
            }
        }


class ErrorResponse(BaseModel):
    """Response de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None