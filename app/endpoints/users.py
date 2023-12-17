from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app.crud import users_crud

from app.dependencies import DB, get_db

users_router = APIRouter()


@users_router.post("/user")
async def new_user(new_user: dict, db: DB = Depends(get_db)):
    try:
        is_exist = await users_crud.check_user_is_exist(db, new_user["email"])
        if is_exist:
            return JSONResponse(
                status_code=400,
                content={"message": "email is exist."},
            )
        db_new_user = await users_crud.insert_new_user(db, new_user)
        return JSONResponse(
            status_code=200,
            content=db_new_user
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@users_router.get("/user/permissions")
async def get_user_permissions(user_id: str, org_id: str, db: DB = Depends(get_db)):
    try:
        role_permissions = await users_crud.query_user_permissions(db, user_id, org_id)
        return JSONResponse(
            status_code=200,
            content=role_permissions
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@users_router.get("/user/basic")
async def get_user_permissions(user_id: str, db: DB = Depends(get_db)):
    try:
        user = await users_crud.query_user_with_id(db, user_id)
        return JSONResponse(
            status_code=200,
            content=user
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@users_router.put("/user/permissions")
async def put_role_user_permissions(data: dict, user_id: str, org_id: str, db: DB = Depends(get_db)):
    try:
        await users_crud.update_user_permissions(db, data, user_id, org_id)
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


@users_router.get("/users")
async def get_users(is_super: bool, user_id: str, role_id: str, db: DB = Depends(get_db)):
    try:
        users = await users_crud.query_users(db, user_id, role_id, is_super)
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


@users_router.post("/user/permissions")
async def new_user_permissions(data: dict, db: DB = Depends(get_db)):
    try:
        await users_crud.insert_user_permissions(db, data)
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


@users_router.get("/user/role/permissions")
async def get_user_role_permissions(user_id: str, db: DB = Depends(get_db)):
    try:
        users = await users_crud.query_user_role_permissions(db, user_id)
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


@users_router.put("/user/basic/{user_id}")
async def update_user_basic(user_id: str, data: dict, db: DB = Depends(get_db)):
    try:
        await users_crud.update_user_basic_with_id(db, data, user_id)
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


@users_router.put("/user/roles/{user_id}")
async def remove_user_roles(data: dict, user_id: str, db: DB = Depends(get_db)):
    try:
        await users_crud.delete_user_roles(db, data, user_id)
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


@users_router.post("/user/role/permissions")
async def new_user_role_permissions(data: dict, user_id: str, db: DB = Depends(get_db)):
    try:
        users = await users_crud.insert_user_role_permissions(db, data, user_id)
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
