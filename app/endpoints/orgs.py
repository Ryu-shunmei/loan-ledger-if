from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app.crud import orgs_crud

from app.dependencies import DB, get_db


orgs_router = APIRouter()


@orgs_router.get("/orgs")
async def get_orgs(role_id: str, db: DB = Depends(get_db)):
    try:
        orgs = await orgs_crud.query_orgs(db, role_id)
        return JSONResponse(
            status_code=200,
            content=orgs
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@orgs_router.post("/org")
async def new_org(data: dict, db: DB = Depends(get_db)):
    try:
        db_new_org = await orgs_crud.insert_org(db, data)
        return JSONResponse(
            status_code=200,
            content=db_new_org
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@orgs_router.get("/org/{org_id}")
async def get_org(org_id: str, db: DB = Depends(get_db)):
    try:
        org = await orgs_crud.query_org(db, org_id)
        return JSONResponse(
            status_code=200,
            content=org
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@orgs_router.put("/org/{org_id}")
async def new_org(org_id: str, data: dict, db: DB = Depends(get_db)):
    try:
        await orgs_crud.update_org(db, data, org_id)
        return JSONResponse(
            status_code=200,
            content={"message": "ok"}
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@orgs_router.post("/org/users/{org_id}")
async def org_new_users(org_id: str, data: dict, db: DB = Depends(get_db)):
    try:
        await orgs_crud.insert_org_users(db, data, org_id)
        return JSONResponse(
            status_code=200,
            content={"message": "ok"}
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@orgs_router.put("/org/users/{org_id}")
async def remove_role_user(data: dict, org_id: str, db: DB = Depends(get_db)):
    try:
        await orgs_crud.delete_org_users(db, data, org_id)
        return JSONResponse(
            status_code=200,
            content={"message": "ok"}
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )
