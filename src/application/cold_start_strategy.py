from neo4j import AsyncSession
from domain.entities import ArtistRecommendation, NewUserProfile

class ColdStartStrategy:
    async def recommend(self, session: AsyncSession, profile: NewUserProfile) -> list[ArtistRecommendation]:
        """
        Executa a inferência de recomendação para um novo utilizador através de Fuzzy Matching,
        exigindo que a vizinhança partilhe pelo menos 2 atributos demográficos/comportamentais.
        """
        query = """
        // 1. Mapeamento flexível dos interesses do novo utilizador
        MATCH (n) WHERE
          (n:Genre AND n.name = $genre) OR
          (n:Mood AND n.name = $mood) OR
          (n:Country AND n.name = $country) OR
          (n:AgeGroup AND n.name = $age_group)
        WITH collect(n) AS target_nodes

        // 2. Fuzzy Matching: Localiza vizinhos com afinidade parcial (>= 2 pontos de contacto)
        MATCH (vizinho:User)-[r]->(trait)
        WHERE trait IN target_nodes
        WITH vizinho, count(r) AS afinidade
        WHERE afinidade >= 2

        // 3. Consolidação da Tribo
        WITH collect(vizinho) AS tribo, count(vizinho) AS total_tribo
        WHERE total_tribo > 0

        // 4. Descoberta de Artistas e Extração de Etiquetas
        UNWIND tribo AS v
        MATCH (v)-[:LISTENS_TO_MOST]->(rec_artist:Artist)

        OPTIONAL MATCH (rec_artist)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (rec_artist)-[:HAS_MOOD]->(m:Mood)

        WITH rec_artist,
             count(DISTINCT v) AS ouvintes,
             total_tribo,
             collect(DISTINCT g.name) + collect(DISTINCT m.name) AS raw_tags

        // Cálculo do peso probabilístico (%)
        RETURN rec_artist.name AS name,
               toInteger(round((toFloat(ouvintes) / total_tribo) * 100)) AS match_percentage,
               raw_tags
        ORDER BY match_percentage DESC
        LIMIT 5
        """

        params = {
            "genre": profile.top_genre,
            "mood": profile.top_mood,
            "country": profile.country,
            "age_group": profile.age_group
        }

        result = await session.run(query, **params)
        records = await result.data()

        recommendations = []
        user_prefs = {profile.top_genre, profile.top_mood}

        for record in records:
            # Limpeza e ordenação de tags (Explainable AI)
            raw_tags = list({tag for tag in record["raw_tags"] if tag})
            raw_tags.sort(key=lambda tag: tag not in user_prefs)

            # Instanciação rigorosa da entidade atualizada
            recommendations.append(ArtistRecommendation(
                name=record["name"],
                match_percentage=record["match_percentage"],
                score=None,
                tags=raw_tags[:5]
            ))

        return recommendations