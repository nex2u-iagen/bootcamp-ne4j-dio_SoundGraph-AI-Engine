from neo4j import AsyncGraphDatabase, AsyncDriver

class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str) -> None:
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver: AsyncDriver | None = None

    async def connect(self) -> None:
        self.__driver = AsyncGraphDatabase.driver(self.__uri, auth=(self.__user, self.__password))

    async def close(self) -> None:
        if self.__driver is not None:
            await self.__driver.close()

    def get_driver(self) -> AsyncDriver:
        if self.__driver is None:
            raise ConnectionError("Driver não inicializado. Execute connect() primeiro.")
        return self.__driver