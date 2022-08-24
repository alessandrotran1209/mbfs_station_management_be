from pydantic import BaseModel


class OperationModel(BaseModel):
    operator: str | None = None
    station_code: str
    date: str
    work_code: str
    old_station_code: str | None = None
    old_date: str | None = None
    old_work_code: str | None = None
    note: str | None = None
