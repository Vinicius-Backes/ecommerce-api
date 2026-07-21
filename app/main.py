from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - garante que os models sejam registrados no Base
from app.routers import auth, users, categories, products, cart, orders

# Cria as tabelas no banco (em produção, prefira usar migrações via Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API REST de um e-commerce simplificado, construída com FastAPI.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/", tags=["Health Check"])
def root():
    """Endpoint simples para checar se a API está no ar."""
    return {"status": "ok", "app": settings.APP_NAME}