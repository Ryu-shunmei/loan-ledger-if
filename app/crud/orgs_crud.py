from providers.psql_provider import DB
from .users_crud import query_user_permissions


async def query_orgs(db: DB, role_id):
    if role_id == "null":
        sql = """
        SELECT
            orgs.id,
            orgs.p_id,
            orgs.name,
            orgs.type,
            users.last_name,
            users.first_name
        FROM
            orgs
        JOIN
            user_org_rels
            ON
            user_org_rels.org_id = orgs.id
        JOIN
            users
            ON
            users.id = user_org_rels.user_id
        WHERE
            user_org_rels.type LIKE '0%';
        """
        return await db.fetch_all(sql)

    sql_main = """
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
    main_org_id = await db.fetch_value(sql_main.format(role_id=role_id))

    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, p_id, name, type FROM orgs WHERE id = '{main_org_id}'
     union
     SELECT child.id, child.p_id, child.name, child.type FROM orgs as child INNER JOIN parents ON parents.id = child.p_id
    )
    SELECT
        parents.id,
        parents.p_id,
        parents.name,
        parents.type,
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
        users.id = user_org_rels.user_id
    WHERE
        user_org_rels.type LIKE '0%';

    """
    return await db.fetch_all(sql)


async def insert_org(db: DB, data: dict):
    sql = f"""
    INSERT INTO orgs (p_id, type, name)
    VALUES (
        '{data["p_id"]}',
        '{data["type"]}',
        '{data["name"]}'
    )
    RETURNING id;
    """
    sql = sql.replace("''", "null")
    new_org = await db.fetch_one(sql)

    sql = f"""
    INSERT INTO roles (type, name)
    VALUES (
        '{data["type"]}',
        '{data["role_name"]}'
    )
    RETURNING id;
    """
    new_role = await db.fetch_one(sql)

    sql = f"""
    INSERT INTO user_org_rels (user_id, org_id, type)
    VALUES (
        '{data["user_id"]}',
        '{new_org["id"]}',
        '{data["type"]}'
    )
    """
    await db.execute(sql)

    sql = f"""
    INSERT INTO user_role_rels (user_id, role_id)
    VALUES (
        '{data["user_id"]}',
        '{new_role["id"]}'
    )
    """
    await db.execute(sql)

    sql = f"""
    INSERT INTO org_role_rels (org_id, role_id)
    VALUES (
        '{new_org["id"]}',
        '{new_role["id"]}'
    )
    """
    await db.execute(sql)

    for permission_id in data["permission_ids"]:
        sql = f"""
        INSERT INTO role_permission_rels (role_id, permission_id)
        VALUES (
            '{new_role["id"]}',
            '{permission_id}'
        )
        """
        await db.execute(sql)

    return new_org


async def query_org(db: DB, org_id: str):
    sql = f"""
    SELECT
        orgs.p_id,
        orgs.name,
        orgs.remark,
        orgs.type,
        user_org_rels.user_id
    FROM
        orgs
    JOIN
        user_org_rels
        ON
        user_org_rels.org_id = orgs.id
    WHERE
        orgs.id = '{org_id}'
        AND
        user_org_rels.type LIKE '0%';
    """

    org_basic = await db.fetch_one(sql)

    sql = f"""
    SELECT
        permissions.id,
        permissions.name
    FROM
        permissions
    JOIN
        role_permission_rels
        ON
        role_permission_rels.permission_id = permissions.id
    JOIN
        roles
        ON
        roles.id = role_permission_rels.role_id
        AND
        roles.type = '{org_basic["type"]}'
    JOIN
        org_role_rels
        ON
        org_role_rels.role_id = roles.id
    WHERE
        org_role_rels.org_id = '{org_id}';
    """

    permissions = await db.fetch_all(sql)

    return {
        **org_basic,
        "permissions": permissions
    }


async def update_org(db: DB, data: dict, org_id: str):
    old_data = await query_org(db, org_id)
    sql = f"""
    SELECT
        id
    FROM
        roles
    JOIN
        org_role_rels
        ON
        org_role_rels.role_id = roles.id
    JOIN
        user_role_rels
        ON
        user_role_rels.role_id = roles.id
    WHERE
        org_role_rels.org_id = '{org_id}'
        AND
        user_role_rels.user_id = '{old_data["user_id"]}';
    """
    old_role_id = await db.fetch_value(sql)

    sql = f"""
    UPDATE orgs
    SET
        p_id = '{data["p_id"]}',
        name = '{data["name"]}',
        type = '{data["type"]}'
    WHERE
        orgs.id = '{org_id}';
    """
    await db.execute(sql)

    if old_data["user_id"] == data["user_id"]:
        sql = f"""
        UPDATE roles
        SET
            name = '{data["role_name"]}',
            type = '{data["type"]}'
        WHERE
            roles.id = '{old_role_id}';
        """
        await db.execute(sql)

        for permission in old_data["permissions"]:
            sql = f"""
            DELETE FROM role_permission_rels
            WHERE
                role_id = '{old_role_id}'
                AND
                permission_id = '{permission["id"]}';
            """
            await db.execute(sql)

        for permission_id in data["permission_ids"]:
            sql = f"""
            INSERT INTO role_permission_rels (role_id, permission_id)
            VALUES (
                '{old_role_id}',
                '{permission_id}'
            )
            """
            await db.execute(sql)

        return
    else:
        sql = f"""
        DELETE FROM user_org_rels
        WHERE
            user_org_rels.user_id = '{old_data["user_id"]}'
            AND
            user_org_rels.org_id = '{org_id}';
        """
        await db.execute(sql)

        sql = f"""
        DELETE FROM user_role_rels
        WHERE
            user_role_rels.user_id = '{old_data["user_id"]}'
            AND
            user_role_rels.role_id = '{old_role_id}';
        """
        await db.execute(sql)

        sql = f"""
        DELETE FROM org_role_rels
        WHERE
            org_role_rels.org_id = '{org_id}'
            AND
            org_role_rels.role_id = '{old_role_id}';
        """
        await db.execute(sql)

        for permission in old_data["permissions"]:
            sql = f"""
            DELETE FROM role_permission_rels
            WHERE
                role_id = '{old_role_id}'
                AND
                permission_id = '{permission["id"]}';
            """
            await db.execute(sql)

        sql = f"""
        DELETE FROM roles WHERE id = '{old_role_id}';
        """
        await db.execute(sql)

        sql = f"""
        INSERT INTO roles (type, name)
        VALUES (
            '{data["type"]}',
            '{data["role_name"]}'
        )
        RETURNING id;
        """
        new_role = await db.fetch_one(sql)

        sql = f"""
        INSERT INTO user_org_rels (user_id, org_id, type)
        VALUES (
            '{data["user_id"]}',
            '{org_id}',
            '{data["type"]}'
        )
        """
        await db.execute(sql)

        sql = f"""
        INSERT INTO user_role_rels (user_id, role_id)
        VALUES (
            '{data["user_id"]}',
            '{new_role["id"]}'
        )
        """
        await db.execute(sql)

        sql = f"""
        INSERT INTO org_role_rels (org_id, role_id)
        VALUES (
            '{org_id}',
            '{new_role["id"]}'
        )
        """
        await db.execute(sql)

        for permission_id in data["permission_ids"]:
            sql = f"""
            INSERT INTO role_permission_rels (role_id, permission_id)
            VALUES (
                '{new_role["id"]}',
                '{permission_id}'
            )
            """
            await db.execute(sql)


async def insert_org_users(db: DB, data: dict, org_id: str):
    org = await query_org(db, org_id)
    for user_id in data["user_ids"]:
        permission_data = data["permissions"][user_id]
        sql = f"""
        INSERT INTO roles (type, name)
        VALUES (
            '{permission_data["type"]}',
            '{permission_data["role_name"]}'
        )
        RETURNING id;
        """
        new_role = await db.fetch_one(sql)

        sql = f"""
        INSERT INTO user_org_rels (user_id, org_id, type)
        VALUES (
            '{user_id}',
            '{org_id}',
            '{permission_data["type"]}'
        )
        """
        await db.execute(sql)

        sql = f"""
        INSERT INTO user_role_rels (user_id, role_id)
        VALUES (
            '{user_id}',
            '{new_role["id"]}'
        )
        """
        await db.execute(sql)

        sql = f"""
        INSERT INTO org_role_rels (org_id, role_id)
        VALUES (
            '{org_id}',
            '{new_role["id"]}'
        )
        """
        await db.execute(sql)

        for permission_id in permission_data["permission_ids"]:
            sql = f"""
            INSERT INTO role_permission_rels (role_id, permission_id)
            VALUES (
                '{new_role["id"]}',
                '{permission_id}'
            )
            """
            await db.execute(sql)


async def delete_org_users(db: DB, data: dict, org_id: str):
    for user_id in data["user_ids"]:
        sql = f"""
        SELECT
            id
        FROM
            roles
        JOIN
            org_role_rels
            ON
            org_role_rels.role_id = roles.id
        JOIN
            user_role_rels
            ON
            user_role_rels.role_id = roles.id
        WHERE
            org_role_rels.org_id = '{org_id}'
            AND
            user_role_rels.user_id = '{user_id}';
        """
        old_role_id = await db.fetch_value(sql)
        old_user_role_permissions = await query_user_permissions(db, user_id, org_id)

        sql = f"""
        DELETE FROM user_org_rels
        WHERE
            user_org_rels.user_id = '{user_id}'
            AND
            user_org_rels.org_id = '{org_id}';
        """
        await db.execute(sql)

        sql = f"""
        DELETE FROM user_role_rels
        WHERE
            user_role_rels.user_id = '{user_id}'
            AND
            user_role_rels.role_id = '{old_role_id}';
        """
        await db.execute(sql)

        sql = f"""
        DELETE FROM org_role_rels
        WHERE
            org_role_rels.org_id = '{org_id}'
            AND
            org_role_rels.role_id = '{old_role_id}';
        """
        await db.execute(sql)

        for permission in old_user_role_permissions["permissions"]:
            sql = f"""
            DELETE FROM role_permission_rels
            WHERE
                role_id = '{old_role_id}'
                AND
                permission_id = '{permission["id"]}';
            """
            await db.execute(sql)

        sql = f"""
        DELETE FROM roles WHERE id = '{old_role_id}';
        """
        await db.execute(sql)
