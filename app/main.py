import string
import time
import random

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from utils.groups import get_group_username, get_group_value

from crud.Operation import Operation
from crud.Station import Station
from crud.Account import Account
from models.ChangePasswordForm import ChangePasswordForm
import utils.Response as re
from fastapi.middleware.cors import CORSMiddleware

from deps import get_current_user
from models.SystemUser import SystemUser
from models.TokenSchema import TokenSchema
from models.UserAuth import UserAuth
from models.UserOut import UserOut
from utils.utils import create_access_token, create_refresh_token, verify_password, get_hashed_password
from geopy.distance import geodesic
import logging
import api
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

app.include_router(api.StationApi.router)
app.include_router(api.OperationApi.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")

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
    print(user)
    operator_name = user.username
    operator_fullname = user.fullname
    role = user.role
    group = user.group if user.group else ''
    if role == 'group leader':
        group = get_group_value(user.username)
    account = Account()
    result = account.get_statistics(
        operator_name, operator_fullname, role, group)
    return re.success_response(data=result)


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
    return re.success_response(data=data, total=total)


@app.get("/statistics/top")
async def get_daily_stats(request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    username = user.username
    role = user.role
    account = Account()
    top_operations = account.get_top_work(username, role)
    return re.success_response(data=top_operations)


@app.post("/change-pw")
async def change_password(request: Request, change_password_form: ChangePasswordForm):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    print(user)
    hashed_pass = user.password
    account = Account()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    if not verify_password(change_password_form.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    result = account.change_password(
        user.username, get_hashed_password(change_password_form.newPassword))
    if result:
        return re.success_response()
    return re.error_response()


@app.post('/insert-update-station')
async def insert_update_station(request: Request):
    try:
        stations = await request.json()
        access_token = request.headers.get('Authorization').split()[-1]
        if access_token == 'null':
            return re.unauthorized_response()
        user = await get_current_user(access_token)
        role = user.role
        if role != 'admin':
            return re.unauthorized_response()

        station = Station()
        operation_result = station.insert_update_stations(stations)
        if operation_result:
            return re.success_response()
    except Exception as e:
        print(str(e))
        return re.error_response()
