from pydantic import BaseModel
from typing import Union

class OperationModel(BaseModel):
    operator: Union[str, None]
    station_code: Union[str, None]
    date: Union[str, None]
    work_code: Union[str, None]
    old_station_code: Union[str, None]
    old_date: Union[str, None]
    old_work_code: Union[str, None]
    note: Union[str, None]
    lat: Union[str, None]
    lng: Union[str, None]
