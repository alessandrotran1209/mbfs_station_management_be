from pydantic import BaseModel

class StationModel(BaseModel):
    station_code: str
    group: str
    region: str
    zone: str
    branch: str
    type: str
    address: str
    lat: str
    lng: str
    district: str
    province: str
    operator: str
    group_leader: str
    phone_number: str
