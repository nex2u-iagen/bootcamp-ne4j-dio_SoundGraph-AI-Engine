from contextlib import asynccontextmanager
from typing import Annotated
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from neo4j import AsyncSession
import uvicorn

# Importações da Arquitetura Modular
from infrastructure.neo4j_connection import Neo4jConnection
from infrastructure.user_repository import UserRepository
from infrastructure.metadata_repository import MetadataRepository, FormMetadata
from application.hybrid_strategy import HybridRecommendationStrategy
from application.cold_start_strategy import ColdStartStrategy
from domain.entities import ArtistRecommendation, UserProfile, NewUserProfile

# Instanciação da Infraestrutura
db = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="minhasenha123")
user_repository = UserRepository()
metadata_repository = MetadataRepository()
hybrid_strategy = HybridRecommendationStrategy()
cold_start_strategy = ColdStartStrategy()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gere a conexão do Neo4j através do ciclo de vida moderno do FastAPI."""
    await db.connect()
    yield
    await db.close()

app = FastAPI(title="SoundGraph AI Engine", version="2.2.1", lifespan=lifespan)

async def get_db_session():
    """Garante sessões assíncronas isoladas por requisição."""
    driver = db.get_driver()
    async with driver.session() as session:
        yield session

# Injeção de Dependências Tipada
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Carrega a interface de usuário de forma segura e multiplataforma."""
    html_path = Path(__file__).resolve().parent / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="index.html não encontrado.")
    return html_path.read_text(encoding="utf-8")

@app.get("/metadata/form", response_model=FormMetadata)
async def get_form_metadata(session: SessionDep):
    """Devolve Gêneros, Humores e Países para preencher os selects do front-end."""
    try:
        return await metadata_repository.get_form_options(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{listener_id}", response_model=UserProfile)
async def get_user_profile(listener_id: int, session: SessionDep):
    """Busca os metadados do usuário existente (Transparência de IA)."""
    try:
        user = await user_repository.get_user_by_id(session, listener_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/{listener_id}", response_model=list[ArtistRecommendation])
async def get_recommendation(listener_id: int, session: SessionDep):
    """Filtragem Híbrida para Usuários Existentes."""
    try:
        recs = await hybrid_strategy.recommend(session, listener_id)
        if not recs:
            raise HTTPException(status_code=404, detail="Sem recomendações para este perfil.")
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/new", response_model=list[ArtistRecommendation])
async def recommend_new_user(profile: NewUserProfile, session: SessionDep):
    """Resolve o Cold Start utilizando o payload simplificado validado pelo Pydantic v2."""
    try:
        recs = await cold_start_strategy.recommend(session, profile)
        if not recs:
            raise HTTPException(status_code=404, detail="Nenhuma tribo encontrada para esta combinação.")
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)