from providers.psql_provider import DB


async def check_user_is_exist(db: DB, email: str):
    sql = f"""
    SELECT
        id
    FROM
        users
    WHERE
        users.email = '{email}';
    """
    return await db.fetch_one(sql)


async def insert_new_user(db: DB, new_user: dict, password: str = "12345678"):
    sql = f"""
    INSERT INTO users
        (
            last_name,
            first_name,
            email,
            password
        )
    VALUES
        (
            '{new_user["last_name"]}',
            '{new_user["first_name"]}',
            '{new_user["email"]}',
            '{password}'
        )
    RETURNING id;
    """
    sql = sql.replace("''", "null")
    return await db.fetch_one(sql)


async def query_user_permissions(db: DB, user_id: str, org_id: str):
    sql = f"""
    SELECT
        id,
        type
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
    role = await db.fetch_one(sql)

    sql = f"""
    SELECT
        id,
        name
    FROM
        permissions
    JOIN
        role_permission_rels
        ON
        role_permission_rels.permission_id = permissions.id
    WHERE
        role_permission_rels.role_id = '{role["id"]}';

    """
    permissions = await db.fetch_all(sql)

    return {
        "type": role["type"],
        "permissions": permissions,
    }


async def update_user_permissions(db: DB, data: dict, user_id: str, org_id: str):
    sql = f"""
    SELECT
        id,
        type
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
    role = await db.fetch_one(sql)

    sql = f"DELETE FROM role_permission_rels WHERE role_permission_rels.role_id = '{role['id']}';"
    await db.execute(sql)

    sql = f"""
    UPDATE roles
    SET
        name = '{data["role_name"]}',
        type = '{data["type"]}'
    WHERE
        roles.id = '{role["id"]}';
    """
    await db.execute(sql)

    sql = f"""
    UPDATE user_org_rels
    SET
        type = '{data["type"]}'
    WHERE
        user_org_rels.user_id = '{user_id}'
        AND
        user_org_rels.org_id = '{org_id}'

    """
    await db.execute(sql)

    for permission_id in data["permission_ids"]:
        sql = f"""
        INSERT INTO role_permission_rels (role_id, permission_id)
        VALUES (
            '{role["id"]}',
            '{permission_id}'
        )
        """
        await db.execute(sql)


async def query_users(db: DB, user_id: str, role_id: str, is_super: bool):
    basic_users = []
    if (is_super):
        sql = """
        SELECT
            id,
            last_name,
            first_name,
            email
        FROM
            users
        WHERE
            users.is_super = false;
        """
        basic_users = await db.fetch_all(sql)
    else:
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
            users.first_name,
            users.email
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
            users.id != '{user_id}';
        """
        basic_users = await db.fetch_all(sql)

    users = []
    for basic_user in basic_users:
        sql = f"""
        SELECT DISTINCT
            roles.id as role_id,
            roles.type as role_type,
            orgs.name as org_name
        FROM
            roles
        JOIN
            org_role_rels
            ON
            org_role_rels.role_id = roles.id
        JOIN
            orgs
            ON
            orgs.id = org_role_rels.org_id
        JOIN
            user_role_rels
            ON
            user_role_rels.role_id = roles.id
        WHERE
            user_role_rels.user_id = '{basic_user["id"]}';
        """
        roles = await db.fetch_all(sql)
        users.append({
            **basic_user,
            "roles": roles,
        })

    return users


async def insert_user_permissions(db: DB, data: dict, password: str = "12345678"):
    sql = f"""
    INSERT INTO users
        (
            last_name,
            first_name,
            email,
            password
        )
    VALUES
        (
            '{data["last_name"]}',
            '{data["first_name"]}',
            '{data["email"]}',
            '{password}'
        )
    RETURNING id;
    """
    new_user = await db.fetch_one(sql)

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
        '{new_user["id"]}',
        '{data["org_id"]}',
        '{data["type"]}'
    )
    """
    await db.execute(sql)

    sql = f"""
    INSERT INTO user_role_rels (user_id, role_id)
    VALUES (
        '{new_user["id"]}',
        '{new_role["id"]}'
    )
    """
    await db.execute(sql)

    sql = f"""
    INSERT INTO org_role_rels (org_id, role_id)
    VALUES (
        '{data["org_id"]}',
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


async def query_user_with_id(db: DB, user_id: str):

    sql = f"""
    SELECT
        last_name,
        first_name,
        email
    FROM
        users
    WHERE
        users.id = '{user_id}';
    """
    return await db.fetch_one(sql)


async def query_user_role_permissions(db: DB, user_id: str):
    sql = f"""
    SELECT
        id,
        last_name,
        first_name,
        email
    FROM
        users
    WHERE
        users.id = '{user_id}';
    """
    basic_user = await db.fetch_one(sql)

    sql = f"""
    SELECT DISTINCT
        roles.id as role_id,
        roles.type as role_type,
        orgs.id as org_id,
        orgs.name as org_name
    FROM
        roles
    JOIN
        org_role_rels
        ON
        org_role_rels.role_id = roles.id
    JOIN
        orgs
        ON
        orgs.id = org_role_rels.org_id
    JOIN
        user_role_rels
        ON
        user_role_rels.role_id = roles.id
    WHERE
        user_role_rels.user_id = '{user_id}';
    """
    roles = await db.fetch_all(sql)
    return {
        **basic_user,
        "roles": roles,
    }


async def update_user_basic_with_id(db: DB, data: dict, user_id: str):
    sql = f"""
    UPDATE users
    SET
        last_name = '{data["last_name"]}',
        first_name = '{data["first_name"]}',
        email = '{data["email"]}'
    WHERE
        users.id = '{user_id}';
    """
    await db.execute(sql)


async def delete_user_roles(db: DB, data: dict, user_id: str):
    for org_id in data["org_ids"]:
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


async def insert_user_role_permissions(db: DB, data: dict, user_id: str):
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
        '{user_id}',
        '{data["org_id"]}',
        '{data["type"]}'
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
        '{data["org_id"]}',
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
