import string
import time
import random

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from crud.Operation import Operation
from crud.Station import Station
from db.MongoConn import MongoConn
from crud.Account import Account
import utils.Response as re
from fastapi.middleware.cors import CORSMiddleware

from deps import get_current_user
from models.Operation import OperationModel
from models.SystemUser import SystemUser
from models.TokenSchema import TokenSchema
from models.UserAuth import UserAuth
from models.UserOut import UserOut
from utils.utils import create_access_token, create_refresh_token, verify_password, get_hashed_password
from geopy.distance import geodesic
import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    # "http://localhost:4200",
    # "https://mobi-hatang.herokuapp.com",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")

    return response

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/statistics")
async def list_stations(request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    operator_fullname = user.fullname
    role = user.role
    account = Account()
    result = account.get_statistics(operator_name, operator_fullname, role)
    return re.success_response(data=result)

@app.get("/station")
async def list_stations(p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    role = user.role
    operator_fullname = user.fullname
    station = Station()
    list_stations, total = station.list_stations(role=role, fullname=operator_fullname, page=p)
    return re.success_response(list_stations, total)


@app.get("/station/station_code")
async def list_operator_station_code(request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    fullname = user.fullname
    role = user.role
    station = Station()
    list_stations_code = station.list_station_code(role=role, fullname=fullname)
    return re.success_response(list_stations_code)


@app.get("/station")
async def list_stations(p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    station = Station()
    list_stations, total = station.list_stations(page=p)
    return re.success_response(list_stations, total)


@app.get("/station/operator")
async def list_stations_code(request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_fullname = user.fullname
    role = user.role
    station = Station()
    list_stations_code = []
    if role == 'operator':
        list_stations_code = station.list_operator_station(operator_fullname)
    elif role == 'group leader':
        list_stations_code = station.list_group_station(operator_fullname)
        logger.info(list_stations_code)
    return re.success_response(list_stations_code)


@app.get("/station/q")
async def search_stations(code: str = '', province: str = '', district: str = '', p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_fullname = user.fullname
    role = user.role
    station = Station()
    list_stations, total = station.search_station(code=code, province=province, district=district, page=p, fullname=operator_fullname, role=role)
    return re.success_response(list_stations, total)


@app.get("/operation")
async def list_operations(p: int, request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    operation = Operation()
    user = await get_current_user(access_token)
    operator_name = user.username
    role = user.role
    list_operations = []
    total = 0
    if role == 'operator':
        list_operations, total = operation.get_operations(operator_name=operator_name, page=p)
    elif role == 'group leader':
        list_operations, total = operation.get_group_operations(operator_name=operator_name, page=p)
    elif role == 'admin':
        list_operations, total = operation.get_all_operations(page=p)
    return re.success_response(list_operations, total)


@app.post("/operation/complete")
async def complete_operation(operation_data: OperationModel, request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    try:
        operation = Operation()
        result = operation.complete_operation(operation_data.dict(), operator_name)
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(e)


@app.get("/operation/q")
async def search_operations(stationCode: str = '', startDate: str = '', endDate: str = '', status: str = '',
                            p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    role = user.role
    operation = Operation()
    list_operations = []
    total = 0
    if role == 'operator':
        list_operations, total = operation.search_operation(operator_name=operator_name, station_code=stationCode,
                                                        start_date=startDate,
                                                        end_date=endDate, status=status, page=p)
    elif role == 'group leader':
        list_operations, total = operation.search_group_operation(operator_name=operator_name, station_code=stationCode,
                                                            start_date=startDate,
                                                            end_date=endDate, status=status, page=p)

    return re.success_response(list_operations, total)


@app.post("/operation/update")
async def update_operation(operation_data: OperationModel, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    try:
        operation = Operation()
        result = operation.update_operation(operation_data.dict(), operator_name)
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(str(e))


@app.put("/operation")
async def insert_operation(operation_data: OperationModel, request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    role = user.role
    # station = Station()
    # station_lat, station_lng = station.get_station_coord(operation_data.station_code)
    # user_lat = operation_data.lat
    # user_lng = operation_data.lng

    # distance = geodesic((station_lat, station_lng), (user_lat,user_lng )).kilometers
    try:
        if role == 'operator':
            operation = Operation()
            result = operation.insert_operation(operation_data.dict(), operator_name)
            if result:
                return re.success_response()
        elif role == 'group leader':
            operation = Operation()
            result = operation.insert_operation_by_group_leader(operation_data.dict(), operator_name)
            if result:
                return re.success_response()
    except Exception as e:
        print(e)
        return re.error_catching(str(e))


@app.post('/signup', summary="Create new user")
async def create_user(data: UserAuth):
    user = {
        'username': data.username,
        'password': get_hashed_password(data.password),
        'fullname': data.fullname
    }
    # saving user to database

    try:
        account = Account()
        result = account.insert_user(user)
        if result:
            return re.success_response(data={
                'username': data.username,
                'password': get_hashed_password(data.password),
            })
    except Exception as e:
        return re.error_catching(e)


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    account = Account()
    user = account.get_user(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    role = account.get_role(form_data.username)
    logger.info(role)
    return {
        "access_token": create_access_token(user['username'], role=role),
        "refresh_token": create_refresh_token(user['username'], role=role),
    }


@app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user


@app.get('/operator')
async def get_in_charge_operator(request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    current_username = user.username
    station = Station()
    list_operators = station.get_operators_by_group_leader(current_username)
    return re.success_response(data=list_operators)


@app.get("/daily-statistics")
async def get_daily_stats():
    operation = Operation()
    data, total = operation.get_group_progress()
    return re.success_response(data = data, total=total)

