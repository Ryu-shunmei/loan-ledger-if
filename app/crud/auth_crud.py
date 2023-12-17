from providers.psql_provider import DB


async def query_user_for_auth(db: DB, email: str):
    sql = f"""
    SELECT
        id,
        email,
        password,
        curr_role_id
    FROM
        users
    WHERE
        users.email = '{email}';
    """
    return await db.fetch_one(sql)


async def query_token_payload(db: DB, user_id):
    sql = f"""
    SELECT
        id,
        email,
        last_name,
        first_name,
        curr_role_id,
        is_super
    FROM
        users
    WHERE
        users.id = '{user_id}';
    """
    user_info = await db.fetch_one(sql)

    sql = f"""
    SELECT
        roles.id,
        roles.type,
        orgs.name as org_name
    FROM
        roles
    JOIN
        user_role_rels
        ON
        user_role_rels.role_id = roles.id
    JOIN
        org_role_rels
        ON
        org_role_rels.role_id = roles.id
    JOIN
        orgs
        ON
        orgs.id = org_role_rels.org_id
    WHERE
        user_role_rels.user_id = '{user_id}';
    """
    roles = await db.fetch_all(sql)

    if user_info["is_super"]:
        sql = f"""
        SELECT DISTINCT
            menus.code,
            menus.name
        FROM
            menus
        JOIN
            permission_menu_rels
            ON
            permission_menu_rels.menu_code = menus.code
        JOIN
            permissions
            ON
            permissions.id = permission_menu_rels.permission_id
        JOIN
            user_permission_rels
            ON
            user_permission_rels.permission_id = permissions.id
        WHERE
            user_permission_rels.user_id = '{user_id}';
        """
        menus_static = await db.fetch_all(sql)

        return {
            **user_info,
            "roles": roles,
            "permission_menus": menus_static
        }
    curr_role_id = None
    if user_info["curr_role_id"] is not None:
        curr_role_id = user_info["curr_role_id"]
    else:
        sql = f"""
        SELECT
            id
        FROM
            roles
        JOIN
            user_role_rels
            ON
            user_role_rels.role_id = roles.id
        WHERE
            user_role_rels.user_id = '{user_id}';
        """
        curr_role_id = await db.fetch_value(sql)
        sql = f"""
        UPDATE users SET curr_role_id = '{curr_role_id}' WHERE users.id = '{user_id}';
        """
        await db.execute(sql)

        sql = f"""
        SELECT
            id,
            email,
            last_name,
            first_name,
            curr_role_id,
            is_super
        FROM
            users
        WHERE
            users.id = '{user_id}';
        """
        user_info = await db.fetch_one(sql)

    sql = f"""
    SELECT DISTINCT
        menus.code,
        menus.name
    FROM
        menus
    JOIN
        permission_menu_rels
        ON
        permission_menu_rels.menu_code = menus.code
    JOIN
        permissions
        ON
        permissions.id = permission_menu_rels.permission_id
    JOIN
        role_permission_rels
        ON
        role_permission_rels.permission_id = permissions.id
    JOIN
        roles
        ON
        roles.id = role_permission_rels.role_id
    JOIN
        user_role_rels
        ON
        user_role_rels.role_id = roles.id
    WHERE
        user_role_rels.user_id = '{user_id}'
        AND
        roles.id = '{curr_role_id}';
    """
    menus_with_role_id = await db.fetch_all(sql)

    sql = f"""
    SELECT
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
    WHERE
        roles.id = '{curr_role_id}';
    """
    curr_role = await db.fetch_one(sql)
    return {
        **user_info,
        "roles": roles,
        "curr_role": curr_role,
        "permission_menus": menus_with_role_id
    }


async def update_user_curr_role_id(db: DB, user_id: str, role_id: str):
    sql = f"""
    UPDATE users SET curr_role_id = '{role_id}' WHERE users.id = '{user_id}';
    """
    await db.execute(sql)
