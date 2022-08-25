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

app = FastAPI()

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    account = Account()
    result = account.get_statistics(operator_name)
    return re.success_response(data=result)

@app.get("/station")
async def list_stations(p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    station = Station()
    list_stations, total = station.list_stations(page=p)
    return re.success_response(list_stations, total)


@app.get("/station/station_code")
async def list_operator_station_code(request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    station = Station()
    list_stations_code = station.list_station_code()
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
    operator_name = user.username
    station = Station()
    list_stations_code = station.list_operator_station(operator_name)
    return re.success_response(list_stations_code)


@app.get("/station/q")
async def search_stations(code: str = '', province: str = '', district: str = '', p: int = 1):
    station = Station()
    list_stations, total = station.search_station(code=code, province=province, district=district, page=p)
    return re.success_response(list_stations, total)


@app.get("/operation")
async def list_operations(p: int, request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    operation = Operation()
    user = await get_current_user(access_token)
    operator_name = user.username
    if operator_name != 'admin':
        list_operations, total = operation.get_operations(operator_name=operator_name, page=p)
    else:
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
        print(e)
        return re.error_catching(e)


@app.get("/operation/q")
async def search_operations(stationCode: str = '', startDate: str = '', endDate: str = '', status: str = '',
                            p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    operation = Operation()
    list_operations, total = operation.search_operation(operator_name=operator_name, station_code=stationCode,
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
        return re.error_catching(e)


@app.put("/operation")
async def insert_operation(operation_data: OperationModel, request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    try:
        operation = Operation()
        result = operation.insert_operation(operation_data.dict(), operator_name)
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(e)


@app.post('/signup', summary="Create new user")
async def create_user(data: UserAuth):
    user = {
        'username': data.username,
        'password': get_hashed_password(data.password),
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
    role = 'admin' if form_data.username == 'admin' else 'operator'
    return {
        "access_token": create_access_token(user['username'], role=role),
        "refresh_token": create_refresh_token(user['username'], role=role),
    }


@app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user
# mongoConn = MongoConn()
# account = Account()
# station = Station()
#
# username = 'thangtv'
# password = 'Mobi$12345'
#
# client = mongoConn.conn()
# # account.authenticate(client, username, password)
# print(station.list_stations(client))
