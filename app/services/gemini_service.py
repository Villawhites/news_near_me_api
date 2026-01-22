import google.generativeai as genai
import json
import re
from typing import List, Optional
from datetime import datetime
from app.core.config import settings
from app.schemas.news import NewsItem, NewsCategory


class GeminiService:
    """Servicio para interactuar con Gemini Pro"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        # ANTES: self.model = genai.GenerativeModel('gemini-pro')
        
        # AHORA: Usamos el modelo más actual y estable
        self.model = genai.GenerativeModel('models/gemini-flash-latest')  
    
    def _build_news_prompt(
        self, 
        location: str, 
        limit: int = 10,
        categories: Optional[List[NewsCategory]] = None,
        language: str = "es"
    ) -> str:
        """Construye el prompt para obtener noticias"""
        
        categories_text = ""
        if categories:
            categories_text = f"\nEnfócate especialmente en estas categorías: {', '.join([c.value for c in categories])}"
        
        prompt = f"""Eres un asistente de noticias experto. Necesito que me proporciones un listado de las {limit} noticias más relevantes que estén sucediendo actualmente cerca de la siguiente ubicación:

**Ubicación:** {location}

{categories_text}

**Instrucciones importantes:**
1. Las noticias deben ser relevantes para esa ubicación específica (ciudad, región o país)
2. Incluye noticias locales, regionales y nacionales que afecten a esa zona
3. Prioriza noticias recientes y de alto impacto
4. El idioma de respuesta debe ser: {language}

**IMPORTANTE: Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin explicaciones.**

El JSON debe tener exactamente esta estructura:
{{
    "news": [
        {{
            "id": 1,
            "title": "Título de la noticia",
            "summary": "Resumen de 2-3 oraciones explicando la noticia",
            "category": "una de: política, economía, deportes, tecnología, entretenimiento, salud, educación, seguridad, medio ambiente, local, otros",
            "relevance_score": 8,
            "location_context": "Por qué es relevante para {location}",
            "estimated_date": "enero 2024",
            "keywords": ["palabra1", "palabra2", "palabra3"]
        }}
    ]
}}

Genera exactamente {limit} noticias ordenadas por relevancia (de mayor a menor).
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[dict]:
        """Parsea la respuesta de Gemini a JSON"""
        try:
            # Limpiar la respuesta de posibles caracteres extra
            cleaned = response_text.strip()
            
            # Intentar encontrar el JSON en la respuesta
            json_match = re.search(r'\{[\s\S]*\}', cleaned)
            if json_match:
                cleaned = json_match.group()
            
            data = json.loads(cleaned)
            return data.get("news", [])
            
        except json.JSONDecodeError as e:
            # Si falla el parsing, intentar extraer información manualmente
            print(f"Error parsing JSON: {e}")
            print(f"Response was: {response_text[:500]}...")
            return []
    
    def _validate_category(self, category: str) -> NewsCategory:
        """Valida y convierte la categoría"""
        category_map = {
            "política": NewsCategory.POLITICS,
            "politica": NewsCategory.POLITICS,
            "economía": NewsCategory.ECONOMY,
            "economia": NewsCategory.ECONOMY,
            "deportes": NewsCategory.SPORTS,
            "tecnología": NewsCategory.TECHNOLOGY,
            "tecnologia": NewsCategory.TECHNOLOGY,
            "entretenimiento": NewsCategory.ENTERTAINMENT,
            "salud": NewsCategory.HEALTH,
            "educación": NewsCategory.EDUCATION,
            "educacion": NewsCategory.EDUCATION,
            "seguridad": NewsCategory.SECURITY,
            "medio ambiente": NewsCategory.ENVIRONMENT,
            "local": NewsCategory.LOCAL,
            "otros": NewsCategory.OTHER,
        }
        return category_map.get(category.lower(), NewsCategory.OTHER)
    
    async def get_news_by_location(
        self,
        location: str,
        limit: int = 10,
        categories: Optional[List[NewsCategory]] = None,
        language: str = "es"
    ) -> List[NewsItem]:
        
        prompt = self._build_news_prompt(location, limit, categories, language)
        
        try:
            response = self.model.generate_content(prompt)
            
            # --- DEBUG PRINTS ---
            print("--- RAW GEMINI RESPONSE ---")
            print(response.text)
            print("---------------------------")
            # --------------------

            raw_news = self._parse_gemini_response(response.text)
            
            news_items = []
            for idx, item in enumerate(raw_news, start=1):
                try:
                    news_item = NewsItem(
                        id=item.get("id", idx),
                        title=item.get("title", "Sin título"),
                        summary=item.get("summary", "Sin resumen disponible"),
                        category=self._validate_category(item.get("category", "otros")),
                        relevance_score=min(max(item.get("relevance_score", 5), 1), 10),
                        location_context=item.get("location_context", location),
                        estimated_date=item.get("estimated_date"),
                        keywords=item.get("keywords", [])
                    )
                    news_items.append(news_item)
                except Exception as e:
                    print(f"Error parsing news item {idx}: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            raise RuntimeError(f"Error comunicándose con Gemini: {str(e)}")


# Singleton
gemini_service = GeminiService()