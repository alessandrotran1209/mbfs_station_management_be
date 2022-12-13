import logging
from fastapi import APIRouter, Request, Depends
from crud.Operation import Operation
from deps import get_current_user, validate_access_token
from utils.groups import get_group_username, get_group_value
import utils.Response as re
from models.Operation import OperationModel

router = APIRouter(prefix="/operation")
logger = logging.getLogger(__name__)


@router.get("")
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
        list_operations, total = operation.get_operations(
            operator_name=operator_name, page=p)
    elif role == 'group leader':
        list_operations, total = operation.get_group_operations(
            operator_name=operator_name, page=p)
    elif role == 'admin':
        list_operations, total = operation.get_all_operations(page=p)
    return re.success_response(list_operations, total)


@router.post("/complete")
async def complete_operation(operation_data: OperationModel, request: Request):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    try:
        operation = Operation()
        result = operation.complete_operation(
            operation_data.dict(), operator_name)
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(e)


@router.get("/q")
async def search_operations(stationCode: str = '', startDate: str = '', endDate: str = '', workCode: str = '', status: str = '', province: str = '', district: str = '',
                            p: int = 1, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    role = user.role
    if operator_name in get_group_username():
        group = get_group_value(operator_name)
    else:
        group = user.group if user.group else ''
    operation = Operation()
    list_operations = []
    total = 0

    list_operations, total = operation.search_admin_operation(group=group, role=role, operator_name=operator_name, station_code=stationCode,
                                                              start_date=startDate, end_date=endDate, work_code=workCode, status=status, page=p, province=province, district=district)

    return re.success_response(list_operations, total)


@router.post("/update")
async def update_operation(operation_data: OperationModel, request: Request = None):
    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    try:
        operation = Operation()
        result = operation.update_operation(
            operation_data.dict(), operator_name)
        if result:
            return re.success_response()
    except Exception as e:
        return re.error_catching(str(e))


@router.put("")
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
            result = operation.insert_operation(
                operation_data.dict(), operator_name)
            if result:
                return re.success_response()
        elif role == 'group leader':
            operation = Operation()
            result = operation.insert_operation_by_group_leader(
                operation_data.dict(), operator_name)
            if result:
                return re.success_response()
    except Exception as e:
        print(e)
        return re.error_catching(str(e))


@router.get("/search_all/q")
async def get_all_operations_on_search(stationCode: str = '', startDate: str = '', endDate: str = '', workCode: str = '', status: str = '', request: Request = None):
    query_params = request.query_params

    access_token = request.headers.get('Authorization').split()[-1]
    if access_token == 'null':
        return re.unauthorized_response()
    user = await get_current_user(access_token)
    operator_name = user.username
    role = user.role
    if operator_name in get_group_username():
        group = get_group_value(operator_name)
    else:
        group = user.group
    operator_fullname = user.fullname
    operation = Operation()
    list_operations = []
    if role == 'operator':
        list_operations = operation.search_all_operation(fullname=operator_fullname, operator_name=operator_name, station_code=stationCode,
                                                         start_date=startDate,
                                                         end_date=endDate, work_code=workCode, status=status)
    elif role == 'group leader':
        list_operations = operation.search_all_group_operation(group=group, station_code=stationCode,
                                                               start_date=startDate,
                                                               end_date=endDate, status=status)
    elif role == 'admin':
        list_operations = operation.search_admin_all_operation(work_code=workCode, station_code=stationCode,
                                                               start_date=startDate,
                                                               end_date=endDate, status=status, province=query_params['province'], district=query_params['district'])
    return re.success_response(list_operations)


@router.get("/zone/q", summary="Search operations on zone scale level")
async def search_zone_operations(request: Request = Depends(validate_access_token)):
    # try:
    operation = Operation()
    list_operations, total = operation.search_zone_operation(
        request.query_params)
    return re.success_response(list_operations, total)
    # except Exception as e:
    #     logger.warning(e)
    #     return re.error_response()
