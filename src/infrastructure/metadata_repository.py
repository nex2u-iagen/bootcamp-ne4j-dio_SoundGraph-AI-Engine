from neo4j import AsyncSession
from pydantic import BaseModel, ConfigDict

class FormMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    genres: list[str]
    moods: list[str]
    countries: list[str]
    age_groups: list[str]

class MetadataRepository:
    async def get_form_options(self, session: AsyncSession) -> FormMetadata:
        query = """
        CALL { MATCH (g:Genre) WITH g.name AS name ORDER BY name RETURN collect(name) AS genres }
        CALL { MATCH (m:Mood) WITH m.name AS name ORDER BY name RETURN collect(name) AS moods }
        CALL { MATCH (c:Country) WITH c.name AS name ORDER BY name RETURN collect(name) AS countries }
        CALL { MATCH (a:AgeGroup) WITH a.name AS name ORDER BY name RETURN collect(name) AS age_groups }
        RETURN genres, moods, countries, age_groups
        """
        result = await session.run(query)
        record = await result.single()
        return FormMetadata(**record.data())