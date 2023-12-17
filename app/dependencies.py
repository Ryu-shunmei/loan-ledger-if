from providers.psql_provider import DB


async def get_db() -> DB:
    return DB()
