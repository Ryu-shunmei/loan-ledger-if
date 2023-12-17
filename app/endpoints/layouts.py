from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app.crud import layouts_crud

from app.dependencies import DB, get_db

layouts_router = APIRouter()


@layouts_router.get("/layouts/orgs")
async def get_orgs(role_id: str, db: DB = Depends(get_db)):
    try:
        orgs = await layouts_crud.query_layouts_orgs(db, role_id)

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


@layouts_router.get("/layouts/users")
async def get_orgs(role_id: str, db: DB = Depends(get_db)):
    try:
        users = await layouts_crud.query_layouts_users(db, role_id)

        return JSONResponse(
            status_code=200,
            content=users
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@layouts_router.get("/layouts/permissions")
async def get_orgs(db: DB = Depends(get_db)):
    try:
        permissions = await layouts_crud.query_layouts_permissions(db)

        return JSONResponse(
            status_code=200,
            content=permissions
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@layouts_router.get("/layouts/org/users")
async def get_orgs(org_id: str, role_id: str, db: DB = Depends(get_db)):
    try:
        users = await layouts_crud.query_layouts_org_users(db, org_id, role_id)

        return JSONResponse(
            status_code=200,
            content=users
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@layouts_router.get("/layouts/users-all")
async def get_orgs(db: DB = Depends(get_db)):
    try:
        users = await layouts_crud.query_layouts_users_all(db)

        return JSONResponse(
            status_code=200,
            content=users
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )
