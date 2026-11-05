from neo4j import AsyncSession
from domain.entities import ArtistRecommendation

class HybridRecommendationStrategy:
    async def recommend(self, session: AsyncSession, listener_id: int) -> list[ArtistRecommendation]:
        # A consulta agora extrai o género e o humor do utilizador alvo no bloco inicial
        query = """
        MATCH (alvo:User {listener_id: $listener_id})
        OPTIONAL MATCH (alvo)-[:PREFERS_GENRE]->(ug:Genre)
        OPTIONAL MATCH (alvo)-[:FEELS]->(um:Mood)
        WITH alvo, ug.name AS user_genre, um.name AS user_mood

        MATCH (alvo)-[:BELONGS_TO_AGE_GROUP]->(ag:AgeGroup)<-[:BELONGS_TO_AGE_GROUP]-(vizinho:User)
        MATCH (alvo)-[:LIVES_IN]->(c:Country)<-[:LIVES_IN]-(vizinho)
        WHERE alvo <> vizinho

        MATCH (vizinho)-[:LISTENS_TO_MOST]->(rec_artist:Artist)
        WHERE NOT (alvo)-[:LISTENS_TO_MOST]->(rec_artist)

        OPTIONAL MATCH (rec_artist)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (rec_artist)-[:HAS_MOOD]->(m:Mood)

        RETURN rec_artist.name AS name,
               count(DISTINCT vizinho) AS score,
               collect(DISTINCT g.name) + collect(DISTINCT m.name) AS raw_tags,
               user_genre,
               user_mood
        ORDER BY score DESC
        LIMIT 5
        """

        result = await session.run(query, listener_id=listener_id)
        records = await result.data()

        recommendations = []
        for record in records:
            # Filtra valores nulos e remove duplicados convertendo para set
            raw_tags = list({tag for tag in record["raw_tags"] if tag})

            # Conjunto de preferências do utilizador para cruzamento em memória
            user_prefs = {record["user_genre"], record["user_mood"]}

            # Ordena as tags: as que existem no perfil do utilizador (user_prefs) aparecem primeiro
            raw_tags.sort(key=lambda tag: tag not in user_prefs)

            # Limita estritamente a 5 tags (Princípio KISS na renderização)
            final_tags = raw_tags[:5]

            # Instanciação rigorosa validada pelo Pydantic v2
            recommendations.append(ArtistRecommendation(
                name=record["name"],
                score=record["score"],
                tags=final_tags
            ))

        return recommendations