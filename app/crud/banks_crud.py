from providers.psql_provider import DB


async def query_banks(db: DB):
    sql = """
    SELECT
        id,
        type,
        name
    FROM
        banks
    """
    return await db.fetch_all(sql)


async def query_bank(db: DB, id: int):
    sql = f"""
    SELECT
        id,
        type,
        name
    FROM
        banks
    WHERE
        banks.id = '{id}';
    """
    return await db.fetch_one(sql)


async def insert_bank(db: DB, bank: dict):
    sql = f"""
    INSERT INTO banks
    (type, name)
    VALUES
    ('{bank["type"]}', '{bank["name"]}');
    """
    sql = sql.replace("'None'", "null").replace("None", "null")

    await db.execute(sql)


async def update_bank(db: DB, bank: dict):
    sql = f"""
    UPDATE
        banks
    SET
        type = '{bank["type"]}',
        name = '{bank["name"]}'
    WHERE
        banks.id = '{bank["id"]}';
    """
    sql = sql.replace("'None'", "null").replace("None", "null")

    await db.execute(sql)
