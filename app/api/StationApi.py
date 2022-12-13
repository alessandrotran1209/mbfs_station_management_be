from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette import status
from pydantic import ValidationError
from jose import jwt
from crud.Station import Station
from deps import get_current_user

from db.MongoConn import MongoConn
import utils.Response as re
from utils.utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)

from models.TokenPayload import TokenPayload

router = APIRouter(prefix="/station")


async def validate_access_token(request: Request):
    try:
        if request.headers.get('Authorization') == None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No access token found"
            )
        access_token = request.headers.get('Authorization').split()[-1]
        if access_token == 'null':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token found"
            )
        payload = jwt.decode(
            access_token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request


@router.get("", summary="Listing operator's assigned stations")
async def list_stations(p: int = 1, request: Request = Depends(get_current_user)):
    user = request
    group = user.group if user.group else ''
    station = Station()
    list_stations, total = station.list_stations(
        role=user.role, fullname=user.fullname, page=p, group=group)
    return re.success_response(list_stations, total)


@router.get("/station_code", summary="Listing operator's assigned stations' district")
async def list_operator_station_code(user: Request = Depends(get_current_user)):
    group = user.group if user.group else ''
    station = Station()
    list_stations_code = station.list_station_code(
        role=user.role, fullname=user.fullname, group=group)
    return re.success_response(list_stations_code)


@router.get("/operator", summary="Listing operator's assigned stations")
async def list_stations_code(request: Request = Depends(get_current_user)):
    user = request
    group = user.group if user.group else ''
    station = Station()
    list_stations_code = []
    if user.role == 'operator':
        list_stations_code = station.list_operator_station(
            user.fullname, group)
    elif user.role == 'group leader':
        list_stations_code = station.list_group_station(user.fullname)
    return re.success_response(list_stations_code)


@router.get("/q", summary="Searching stations by code, province, district")
async def search_stations(code: str = '', province: str = '', district: str = '', p: int = 1, user: Request = Depends(get_current_user), request: Request = None):
    print(request.query_params['province'])

    operator_fullname = user.fullname
    role = user.role
    group = user.group if user.group else ''
    station = Station()
    list_stations, total = station.search_station(
        code=code, province=province, district=district, page=p, fullname=operator_fullname, role=role, group=group)
    return re.success_response(list_stations, total)


@router.get('/suggestion/q', summary="Listing all stations on character match")
async def get_station_suggestion(request: Request = Depends(validate_access_token)):
    mongo_conn = MongoConn()
    client = mongo_conn.conn()
    station_collection = client['station']

    list_station_code = station_collection.distinct('station_code',
                                                    {"station_code": {
                                                        "$regex": request.query_params['code']}}
                                                    )

    return re.success_response(list_station_code)


@router.get('/prefetch', summary="Prefetch data for admin search in report")
async def get_station_suggestion(request: Request = Depends(validate_access_token)):
    try:
        station = Station()
        ret_data = station.prefetch_search_data()
        return re.success_response(ret_data)
    except:
        return re.error_response()


@router.get('/prefetch/q', summary="Prefetch data for admin search in report filtered by zone")
async def get_station_suggestion(zone: str, request: Request = Depends(validate_access_token)):
    try:
        station = Station()
        ret_data = station.prefetch_zone_search_data(zone)
        return re.success_response(ret_data)
    except:
        return re.error_response()
