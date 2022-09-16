from pydantic import BaseModel


class OperationModel(BaseModel):
    operator: str
    station_code: str
    date: str
    work_code: str
    old_station_code: str
    old_date: str
    old_work_code: str
    note: str
    lat: str
    lng: str
