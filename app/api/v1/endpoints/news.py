from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime

from app.schemas import (
    NewsRequest,
    NewsResponse,
    NewsCategory,
    ErrorResponse,
    LocationResponse
)
from app.services import geolocation_service, gemini_service

router = APIRouter()


@router.get(
    "/",
    response_model=NewsResponse,
    responses={
        200: {
            "description": "Noticias obtenidas exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "location": "Santiago, Región Metropolitana, Chile",
                        "generated_at": "2024-01-22T15:30:00Z",
                        "total_news": 3,
                        "news": [
                            {
                                "id": 1,
                                "title": "Metro anuncia nueva extensión",
                                "summary": "La línea 7 llegará a nuevas comunas...",
                                "category": "local",
                                "relevance_score": 9,
                                "location_context": "Afecta transporte en Santiago",
                                "estimated_date": "enero 2024",
                                "keywords": ["metro", "transporte"]
                            }
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Error en los parámetros de la solicitud",
            "model": ErrorResponse
        },
        503: {
            "description": "Servicio de geolocalización no disponible",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    },
    summary="Obtener noticias por ubicación automática",
    description="Obtiene noticias relevantes basadas en tu ubicación detectada automáticamente por IP."
)
async def get_news(
    request: Request,
    limit: int = Query(
        default=10, 
        ge=1, 
        le=20, 
        description="Número máximo de noticias a retornar",
        examples=[5, 10, 15]
    ),
    categories: Optional[List[NewsCategory]] = Query(
        default=None, 
        description="Filtrar por categorías específicas"
    ),
    language: str = Query(
        default="es", 
        description="Código de idioma para las noticias",
        examples=["es", "en"]
    )
):
    """
    Obtiene noticias relevantes para la ubicación detectada automáticamente.
    
    - **limit**: Número de noticias (1-20)
    - **categories**: Filtrar por categorías específicas
    - **language**: Idioma de las noticias (es, en, etc.)
    """
    try:
        # 1. Debug IP
        client_ip = request.client.host
        print(f"DEBUG: Client IP -> {client_ip}") 
        
        if client_ip in ["127.0.0.1", "localhost", "::1"]:
            client_ip = None
        
        # 2. Debug Location
        location = await geolocation_service.get_location_by_ip(client_ip)
        location_string = geolocation_service.format_location_string(location)
        print(f"DEBUG: Location detected -> {location_string}")
        
        # 3. Debug Gemini
        print(f"DEBUG: Calling Gemini...")
        news = await gemini_service.get_news_by_location(
            location=location_string,
            limit=limit,
            categories=categories,
            language=language
        )
        print(f"DEBUG: News received -> {len(news)}")
        
        return NewsResponse(
            success=True,
            location=location_string,
            generated_at=datetime.utcnow(),
            total_news=len(news),
            news=news
        )
        
    except ValueError as e:
        print(f"ERROR VALUE: {str(e)}")  # <--- ESTO SALDRÁ EN TU TERMINAL
        raise HTTPException(status_code=400, detail=f"Error de valor: {str(e)}")
    except ConnectionError as e:
        print(f"ERROR CONEXION: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error de conexión: {str(e)}")
    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc() # Imprime el error completo
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post(
    "/",
    response_model=NewsResponse,
    responses={
        200: {"description": "Noticias obtenidas exitosamente"},
        400: {"description": "Ubicación no proporcionada", "model": ErrorResponse},
        500: {"description": "Error interno", "model": ErrorResponse}
    },
    summary="Obtener noticias con ubicación personalizada",
    description="Obtiene noticias relevantes basadas en una ubicación proporcionada manualmente."
)
async def get_news_custom_location(news_request: NewsRequest):
    """
    Obtiene noticias para una ubicación proporcionada manualmente.
    
    Útil cuando quieres buscar noticias de una ciudad diferente a tu ubicación actual.
    """
    try:
        location_parts = [
            news_request.city,
            news_request.region,
            news_request.country
        ]
        location_string = ", ".join(filter(None, location_parts))
        
        if not location_string:
            raise ValueError("Debes proporcionar al menos ciudad, región o país")
        
        news = await gemini_service.get_news_by_location(
            location=location_string,
            limit=news_request.limit,
            categories=news_request.categories,
            language=news_request.language
        )
        
        return NewsResponse(
            success=True,
            location=location_string,
            generated_at=datetime.utcnow(),
            total_news=len(news),
            news=news
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/location",
    response_model=LocationResponse,
    responses={
        200: {
            "description": "Ubicación detectada exitosamente",
            "content": {
                "application/json": {
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
            }
        },
        500: {"description": "Error detectando ubicación", "model": ErrorResponse}
    },
    summary="Ver ubicación detectada",
    description="Muestra la ubicación detectada basándose en la IP del cliente."
)
async def get_detected_location(request: Request):
    """
    Retorna la ubicación detectada basada en la IP del cliente.
    
    Útil para debugging y verificar qué ubicación está usando el sistema.
    """
    try:
        client_ip = request.client.host
        
        if client_ip in ["127.0.0.1", "localhost", "::1"]:
            client_ip = None
        
        location = await geolocation_service.get_location_by_ip(client_ip)
        return location
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/categories",
    response_model=List[dict],
    summary="Listar categorías disponibles",
    description="Retorna todas las categorías de noticias disponibles para filtrar."
)
async def get_categories():
    """
    Lista todas las categorías de noticias disponibles.
    """
    return [
        {"value": category.value, "name": category.name}
        for category in NewsCategory
    ]