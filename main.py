from fastapi import FastAPI

from crud.Operation import Operation
from crud.Station import Station
from db.MongoConn import MongoConn
from crud.Account import Account
import utils.Response as re
from fastapi.middleware.cors import CORSMiddleware
from models.Operation import OperationModel

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


@app.get("/station")
async def list_stations(p: int = 1):
    station = Station()
    list_stations, total = station.list_stations(page=p)
    return re.success_response(list_stations, total)


@app.get("/station/station_code")
async def list_stations_code():
    station = Station()
    list_stations_code = station.list_station_code()
    return re.success_response(list_stations_code)


@app.get("/station/q")
async def search_stations(code: str = '', province: str = '', p: int = 1):
    station = Station()
    list_stations, total = station.search_station(code=code, province=province, page=p)
    return re.success_response(list_stations, total)


@app.get("/operation")
async def list_operations(p: int = 1):
    operation = Operation()
    list_operations, total = operation.get_operations(operator_name='thangtv', page=p)
    return re.success_response(list_operations, total)

@app.post("/operation/complete")
async def complete_operation(operation_data: OperationModel):
    try:
        operation = Operation()
        result = operation.complete_operation(operation_data.dict())
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(e)


@app.get("/operation/q")
async def search_operations(stationCode:str='', startDate: str='', endDate: str='', p:int =1):
    operation = Operation()
    list_operations, total = operation.search_operation(station_code=stationCode, start_date=startDate, end_date=endDate, page=p)
    return re.success_response(list_operations, total)


@app.post("/operation/update")
async def update_operation(operation_data: OperationModel):
    try:
        operation = Operation()
        result = operation.update_operation(operation_data.dict())
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(e)

@app.put("/operation")
async def insert_operation(operation_data: OperationModel):
    try:
        operation = Operation()
        result = operation.insert_operation(operation_data.dict())
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(e)

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
