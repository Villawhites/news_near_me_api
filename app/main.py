from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## 🗞️ News Near Me API

API inteligente que proporciona noticias relevantes basadas en tu ubicación actual, 
potenciada por **Gemini Pro AI**.

### ✨ Características principales:

- 📍 **Detección automática de ubicación** - Identifica tu ciudad, región y país por IP
- 🤖 **IA Generativa** - Usa Gemini Pro para curar y resumir noticias relevantes
- 🏷️ **Categorización inteligente** - Noticias organizadas por: política, economía, deportes, tecnología, etc.
- 🌍 **Multiidioma** - Soporte para múltiples idiomas
- ⚡ **Tiempo real** - Noticias actualizadas al momento de la consulta

### 🔗 Enlaces útiles:

- [Documentación completa](/docs)
- [ReDoc](/redoc)
- [GitHub Repository](https://github.com/tu-usuario/news-near-me-api)

### 📧 Contacto:

Para soporte o consultas: tu-email@ejemplo.com
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    contact={
        "name": "Tu Nombre",
        "url": "https://tu-sitio-web.com",
        "email": "tu-email@ejemplo.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "News",
            "description": "Operaciones relacionadas con la obtención de noticias personalizadas por ubicación.",
            "externalDocs": {
                "description": "Más información sobre Gemini",
                "url": "https://ai.google.dev/",
            },
        },
        {
            "name": "Health",
            "description": "Endpoints para verificar el estado de la API.",
        },
        {
            "name": "Root",
            "description": "Endpoint raíz de bienvenida.",
        },
    ]
)


# Custom OpenAPI schema (opcional, para mayor personalización)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        contact=app.contact,
        license_info=app.license_info,
    )
    
    # Personalizar el logo (opcional)
    openapi_schema["info"]["x-logo"] = {
        "url": "https://tu-dominio.com/logo.png",
        "altText": "News Near Me Logo"
    }
    
    # Agregar servidores - producción primero para Swagger
    openapi_schema["servers"] = [
        {
            "url": "/",
            "description": "Servidor actual (auto-detectado)"
        },
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo local"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"], summary="Bienvenida", description="Endpoint de bienvenida a la API")
async def root():
    """
    ## 👋 Bienvenido a News Near Me API
    
    Este endpoint muestra información básica de la API.
    
    Para ver la documentación completa, visita `/docs` o `/redoc`.
    """
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/api/v1/openapi.json"
        }
    }