from providers.psql_provider import DB


async def query_cases(db: DB, role_id: str):
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
        cases.id,
        cases.org_id,
        cases.user_id,
        cases.execute_confirm,
        cases.shbs_report,
        cases.bank_id,
        cases.loan_target,
        cases.ap_loan_applicable,
        cases.excute_date,
        cases.house_code,
        cases.house_name,
        cases.loan_amount,
        cases.deduction_amount,
        cases.deposit_amount,
        cases.heim_note,
        cases.shbs_note,
        cases.shbs_confirm,
        cases.collection_date,
        cases.receive_date,
        cases.registrate_date,
        cases.schedule_date,
        cases.establish_date,
        cases.doc_send_date,
        cases.confirm_date,
        users.last_name,
        users.first_name,
        orgs.name as org_name,
        banks.name as bank_name,
        banks.type
    FROM
        parents
    JOIN
        cases
        ON
        cases.org_id = parents.id
    JOIN
        orgs
        ON
        orgs.id = cases.org_id
    JOIN
        users
        ON
        users.id = cases.user_id
    JOIN
        banks
        ON
        banks.id = cases.bank_id;
    """
    return await db.fetch_all(sql)


async def insert_case(db: DB, data: dict):
    sql = f"""
    INSERT INTO cases
        (
            org_id,
            user_id,
            execute_confirm,
            shbs_report,
            bank_id,
            loan_target,
            ap_loan_applicable,
            excute_date,
            house_code,
            house_name,
            loan_amount,
            deduction_amount,
            deposit_amount,
            heim_note,
            shbs_note,
            shbs_confirm,
            collection_date,
            receive_date,
            registrate_date,
            schedule_date,
            establish_date,
            doc_send_date,
            confirm_date
        )
    VALUES
        (
            '{data["org_id"]}',
            '{data["user_id"]}',
            '{data["execute_confirm"]}',
            '{data["shbs_report"]}',
            '{data["bank_id"]}',
            '{data["loan_target"]}',
            '{data["ap_loan_applicable"]}',
            '{data["excute_date"]}',
            '{data["house_code"]}',
            '{data["house_name"]}',
            {data["loan_amount"]},
            {int(data["loan_amount"])-int(data["deposit_amount"])},
            {data["deposit_amount"]},
            '{data["heim_note"]}',
            '{data["shbs_note"]}',
            '{data["shbs_confirm"]}',
            '{data["collection_date"]}',
            '{data["receive_date"]}',
            '{data["registrate_date"]}',
            '{data["schedule_date"]}',
            '{data["establish_date"]}',
            '{data["doc_send_date"]}',
            '{data["confirm_date"]}'
        );
    """
    sql = sql.replace("''", "null")
    await db.execute(sql)


async def query_case(db: DB, id: int):
    sql = f"""
    SELECT
        cases.id,
        cases.org_id,
        cases.user_id,
        cases.execute_confirm,
        cases.shbs_report,
        cases.bank_id,
        cases.loan_target,
        cases.ap_loan_applicable,
        cases.excute_date,
        cases.house_code,
        cases.house_name,
        cases.loan_amount,
        cases.deduction_amount,
        cases.deposit_amount,
        cases.heim_note,
        cases.shbs_note,
        cases.shbs_confirm,
        cases.collection_date,
        cases.receive_date,
        cases.registrate_date,
        cases.schedule_date,
        cases.establish_date,
        cases.doc_send_date,
        cases.confirm_date
    FROM
        cases
    WHERE
        cases.id = '{id}';
    """

    return await db.fetch_one(sql)


async def update_case(db: DB, data: dict):
    sql = f"""
    UPDATE 
        cases
    SET
        org_id = '{data["org_id"]}',
        user_id = '{data["user_id"]}',
        execute_confirm = '{data["execute_confirm"]}',
        shbs_report = '{data["shbs_report"]}',
        bank_id = '{data["bank_id"]}',
        loan_target = '{data["loan_target"]}',
        ap_loan_applicable = '{data["ap_loan_applicable"]}',
        excute_date = '{data["excute_date"]}',
        house_code = '{data["house_code"]}',
        house_name = '{data["house_name"]}',
        loan_amount = {data["loan_amount"]},
        deduction_amount = {int(data["loan_amount"])-int(data["deposit_amount"])},
        deposit_amount = {data["deposit_amount"]},
        heim_note = '{data["heim_note"]}',
        shbs_note = '{data["shbs_note"]}',
        shbs_confirm = '{data["shbs_confirm"]}',
        collection_date = '{data["collection_date"]}',
        receive_date = '{data["receive_date"]}',
        registrate_date = '{data["registrate_date"]}',
        schedule_date = '{data["schedule_date"]}',
        establish_date = '{data["establish_date"]}',
        doc_send_date = '{data["doc_send_date"]}',
        confirm_date = '{data["confirm_date"]}'
    WHERE
        cases.id = '{data["id"]}'
    """
    sql = sql.replace("''", "null")
    await db.execute(sql)
