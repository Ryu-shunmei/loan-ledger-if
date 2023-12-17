from providers.psql_provider import DB


async def query_layouts_orgs(db: DB, role_id: str):

    sql_main = f"""
    SELECT
        orgs.id
    FROM
        orgs
    JOIN
        org_role_rels
        ON
        org_role_rels.org_id = orgs.id
    WHERE
        org_role_rels.role_id = '{role_id}';
    """
    main_org_id = await db.fetch_value(sql_main)

    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, p_id, name, type FROM orgs WHERE id = '{main_org_id}'
     union
     SELECT child.id, child.p_id, child.name, child.type FROM orgs as child INNER JOIN parents ON parents.id = child.p_id
    )
    SELECT
        parents.id,
        parents.name
    FROM
        parents;

    """
    return await db.fetch_all(sql)


async def query_layouts_users(db: DB, role_id: str):

    sql = f"""
    SELECT
        orgs.id
    FROM
        orgs
    JOIN
        org_role_rels
        ON
        org_role_rels.org_id = orgs.id
    WHERE
        org_role_rels.role_id = '{role_id}';
    """
    main_org_id = await db.fetch_value(sql)

    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, p_id, name, type FROM orgs WHERE id = '{main_org_id}'
     union
     SELECT child.id, child.p_id, child.name, child.type FROM orgs as child INNER JOIN parents ON parents.id = child.p_id
    )
    SELECT DISTINCT
        users.id,
        users.last_name,
        users.first_name
    FROM
        parents
    JOIN
        user_org_rels
        ON
        user_org_rels.org_id = parents.id
    JOIN
        users
        ON
        users.id = user_org_rels.user_id;
    """
    return await db.fetch_all(sql)


async def query_layouts_users_all(db: DB):
    sql = f"""
    SELECT
        users.id,
        users.last_name,
        users.first_name
    FROM
        users
    WHERE
        users.is_super = false;
    """
    return await db.fetch_all(sql)


async def query_layouts_permissions(db: DB):
    sql = """
    SELECT
        id,
        name
    FROM
        permissions;
    """
    return await db.fetch_all(sql)


async def query_layouts_org_users(db: DB, org_id: str, role_id: str):
    sql = f"""
    SELECT
        users.id,
        users.last_name,
        users.first_name,
        users.email,
        user_org_rels.org_id,
        user_org_rels.type
    FROM
        users
    JOIN
        user_org_rels
        ON
        user_org_rels.user_id = users.id
    WHERE
        users.is_super = false
        AND
        user_org_rels.org_id = '{org_id}'
        AND
        user_org_rels.type NOT LIKE '0%';
    """
    org_users = await db.fetch_all(sql)

    sql = f"""
    SELECT
        users.id,
        users.last_name,
        users.first_name,
        users.email,
        user_org_rels.org_id,
        user_org_rels.type
    FROM
        users
    JOIN
        user_org_rels
        ON
        user_org_rels.user_id = users.id
    WHERE
        users.is_super = false
        AND
        user_org_rels.org_id = '{org_id}';
    """
    _org_users = await db.fetch_all(sql)

    sql = f"""
    SELECT
        orgs.id
    FROM
        orgs
    JOIN
        org_role_rels
        ON
        org_role_rels.org_id = orgs.id
    WHERE
        org_role_rels.role_id = '{role_id}';
    """
    main_org_id = await db.fetch_value(sql)

    sql = f"""
    SELECT
        users.id,
        users.last_name,
        users.first_name
    FROM
        users
    WHERE
        users.is_super = false;
    """
    all_users = await db.fetch_all(sql)
    org_users_ids = [i["id"] for i in _org_users]
    other_users = []
    for other_user in all_users:
        if other_user["id"] not in org_users_ids:
            other_users.append(other_user)
    return {
        "org_users": org_users,
        "other_users": other_users,
    }
