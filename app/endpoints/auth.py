from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app.crud import auth_crud

from app.dependencies import DB, get_db
from utils.jwt import gen_access_token


auth_router = APIRouter()


@auth_router.post("/token")
async def auth_for_token(auth_user: dict, db: DB = Depends(get_db)):
    try:
        db_user = await auth_crud.query_user_for_auth(db, auth_user["email"])
        if db_user is None:
            return JSONResponse(
                status_code=400,
                content={"message": "email is not exist."},
            )
        if db_user["password"] != auth_user["password"]:
            return JSONResponse(
                status_code=400,
                content={"message": "password or email is error."},
            )
        payload = await auth_crud.query_token_payload(db, db_user["id"])
        access_token = gen_access_token(payload=payload)
        return JSONResponse(
            status_code=200,
            content={"access_token": access_token}
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@auth_router.put("/token")
async def update_token(user_id: str, role_id: str, db: DB = Depends(get_db)):
    try:
        await auth_crud.update_user_curr_role_id(db, user_id, role_id)
        payload = await auth_crud.query_token_payload(db, user_id)
        access_token = gen_access_token(payload=payload)
        return JSONResponse(
            status_code=200,
            content={"access_token": access_token}
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )


@auth_router.get("/token")
async def update_token(user_id: str, db: DB = Depends(get_db)):
    try:
        payload = await auth_crud.query_token_payload(db, user_id)
        access_token = gen_access_token(payload=payload)
        return JSONResponse(
            status_code=200,
            content={"access_token": access_token}
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."}
        )
