from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from app.crud import cases_crud

from app.dependencies import DB, get_db


cases_router = APIRouter()


@cases_router.get("/cases")
async def get_banks(role_id: str, db: DB = Depends(get_db)):
    try:
        cases = await cases_crud.query_cases(db, role_id)
        return JSONResponse(
            status_code=200,
            content=cases
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."},
        )


@cases_router.get("/case/{case_id}")
async def get_banks(case_id: str, db: DB = Depends(get_db)):
    try:
        case = await cases_crud.query_case(db, case_id)
        return JSONResponse(
            status_code=200,
            content=case
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."},
        )


@cases_router.post("/case")
async def get_banks(data: dict, db: DB = Depends(get_db)):
    try:
        await cases_crud.insert_case(db, data)
        return JSONResponse(
            status_code=200,
            content={"message": "ok"},
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."},
        )


@cases_router.put("/case")
async def get_banks(data: dict, db: DB = Depends(get_db)):
    try:
        await cases_crud.update_case(db, data)
        return JSONResponse(
            status_code=200,
            content={"message": "ok"},
        )
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unknown exception occurred, please try again later."},
        )
