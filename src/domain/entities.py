from pydantic import BaseModel, ConfigDict, Field

class ArtistRecommendation(BaseModel):
    """
    Entidade de saída unificada.
    Utiliza tipagem opcional (int | None) para suportar tanto o score absoluto
    (usuários existentes) quanto o percentual (novos usuários).
    """
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Nome do artista sugerido")
    # Tornamos os campos de pontuação opcionais (None por padrão)
    score: int | None = Field(default=None, description="Força da similaridade baseada no perfil")
    match_percentage: int | None = Field(default=None, description="Probabilidade percentual de afinidade (0-100%)")
    tags: list[str] = Field(default_factory=list, description="Etiquetas de Explainable AI")

class UserProfile(BaseModel):
    """Metadados do usuário existente extraídos do grafo."""
    model_config = ConfigDict(from_attributes=True)

    listener_id: int = Field(..., description="ID único do ouvinte")
    age: int = Field(..., description="Idade do usuário")
    country: str = Field(default="Não informado", description="País de residência")
    platform: str = Field(default="Não informado", description="Plataforma principal")
    top_genre: str = Field(default="Não informado", description="Gênero favorito")
    top_artist: str = Field(default="Não informado", description="Artista mais ouvido")
    top_mood: str = Field(default="Não informado", description="Humor principal")

class NewUserProfile(BaseModel):
    """
    Payload otimizado para resolver o Cold Start (Fuzzy Matching).
    O Pydantic garante que não receberemos strings vazias da interface web.
    """
    model_config = ConfigDict(from_attributes=True)

    top_genre: str = Field(..., min_length=2, description="Gênero musical selecionado")
    top_mood: str = Field(..., min_length=2, description="Humor selecionado")
    country: str = Field(..., min_length=2, description="País de residência selecionado")
    age_group: str = Field(..., min_length=2, description="Faixa etária exata mapeada no grafo")