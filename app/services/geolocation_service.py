import httpx
from typing import Optional
from app.core.config import settings
from app.schemas.location import LocationResponse


class GeolocationService:
    """Servicio para obtener la ubicación del usuario"""
    
    def __init__(self):
        self.api_url = settings.geolocation_api_url
    
    async def get_location_by_ip(self, ip: Optional[str] = None) -> LocationResponse:
        """
        Obtiene la ubicación basada en la IP.
        Si no se proporciona IP, usa la IP del cliente.
        """
        url = f"{self.api_url}/{ip}" if ip else self.api_url
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "fail":
                    raise ValueError(f"Error de geolocalización: {data.get('message')}")
                
                return LocationResponse(
                    city=data.get("city", "Unknown"),
                    region=data.get("regionName", "Unknown"),
                    country=data.get("country", "Unknown"),
                    country_code=data.get("countryCode"),
                    latitude=data.get("lat"),
                    longitude=data.get("lon"),
                    ip=data.get("query"),
                    timezone=data.get("timezone")
                )
                
            except httpx.HTTPError as e:
                raise ConnectionError(f"Error conectando al servicio de geolocalización: {str(e)}")
    
    def format_location_string(self, location: LocationResponse) -> str:
        """Formatea la ubicación como string legible"""
        parts = [location.city, location.region, location.country]
        return ", ".join(filter(lambda x: x and x != "Unknown", parts))


# Singleton
geolocation_service = GeolocationService()