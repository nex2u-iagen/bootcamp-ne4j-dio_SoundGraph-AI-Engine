from neo4j import AsyncSession
from domain.entities import ArtistRecommendation
from application.recommendation_strategy import RecommendationStrategy

class CollaborativeGenreStrategy(RecommendationStrategy):
    async def recommend(self, session: AsyncSession, listener_id: int) -> list[ArtistRecommendation]:
        query = """
        MATCH (target:User {listener_id: $listener_id})-[:PREFERS_GENRE]->(g:Genre)
        MATCH (other:User)-[:PREFERS_GENRE]->(g)
        WHERE target <> other
        MATCH (other)-[:LISTENS_TO_MOST]->(rec_artist:Artist)
        WHERE NOT (target)-[:LISTENS_TO_MOST]->(rec_artist)
        RETURN rec_artist.name AS name, count(other) AS score
        ORDER BY score DESC
        LIMIT 5
        """
        result = await session.run(query, listener_id=listener_id)
        records = await result.data()

        return [ArtistRecommendation(**record) for record in records]