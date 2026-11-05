from neo4j import AsyncSession
from domain.entities import UserProfile

class UserRepository:
    async def get_user_by_id(self, session: AsyncSession, listener_id: int) -> UserProfile | None:
        """
        Consulta o nó do usuário e expande seus relacionamentos para montar o perfil completo.
        Utiliza OPTIONAL MATCH para não quebrar a consulta caso falte alguma aresta.
        """
        query = """
        MATCH (u:User {listener_id: $listener_id})
        OPTIONAL MATCH (u)-[:LIVES_IN]->(c:Country)
        OPTIONAL MATCH (u)-[:USES]->(p:Platform)
        OPTIONAL MATCH (u)-[:PREFERS_GENRE]->(g:Genre)
        OPTIONAL MATCH (u)-[:LISTENS_TO_MOST]->(a:Artist)
        OPTIONAL MATCH (u)-[:FEELS]->(m:Mood)
        RETURN u.listener_id AS listener_id,
               u.age AS age,
               c.name AS country,
               p.name AS platform,
               g.name AS top_genre,
               a.name AS top_artist,
               m.name AS top_mood
        """
        result = await session.run(query, listener_id=listener_id)
        record = await result.single()

        if not record:
            return None

        return UserProfile(**record.data())