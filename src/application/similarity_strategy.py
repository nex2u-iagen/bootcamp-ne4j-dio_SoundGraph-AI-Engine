# src/application/similarity_strategy.py
from neo4j import AsyncSession
from domain.entities import ArtistRecommendation

class ProfileSimilarityStrategy:
    async def recommend(self, session: AsyncSession, listener_id: int) -> list[ArtistRecommendation]:
        query = """
        MATCH (alvo:User {listener_id: $listener_id})-[:FEELS]->(m:Mood)<-[:FEELS]-(vizinho:User)
        MATCH (alvo)-[:LIVES_IN]->(c:Country)<-[:LIVES_IN]-(vizinho)
        WHERE alvo <> vizinho
        MATCH (vizinho)-[:LISTENS_TO_MOST]->(rec_artist:Artist)
        WHERE NOT (alvo)-[:LISTENS_TO_MOST]->(rec_artist)
        RETURN rec_artist.name AS name, count(vizinho) AS score
        ORDER BY score DESC
        LIMIT 5
        """
        result = await session.run(query, listener_id=listener_id)
        records = await result.data()

        return [ArtistRecommendation(**record) for record in records]