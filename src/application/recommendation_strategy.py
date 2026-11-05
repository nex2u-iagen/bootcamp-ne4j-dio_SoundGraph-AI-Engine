from typing import Protocol
from neo4j import AsyncSession
from domain.entities import ArtistRecommendation

class RecommendationStrategy(Protocol):
    async def recommend(self, session: AsyncSession, listener_id: int) -> list[ArtistRecommendation]:
        """Interface para estratégias de recomendação musical."""
        ...