from datetime import datetime, timezone
from ..core.config import MAKSIMUM_WAKTU_DEVICE
from fastapi import APIRouter, status, Depends
from sqlmodel import SQLModel
from ..auth.dependency import require_role

router = APIRouter(prefix='/devices', tags=['devices'], dependencies=[Depends(require_role("admin"))])
devices = {}

#model
class DeviceRequest(SQLModel):
    id_device: str
    kualitas_rssi_perangkat: int | None = None

class DeviceResponse(SQLModel):
    id_device: str
    waktu_request_terakhir: datetime | None = None
    kualitas_rssi_perangkat: int | None = None
    status_perangkat: bool = False

#endpoint
@router.post('/heartbeat', status_code=status.HTTP_200_OK)
def esp_ke_server(form: DeviceRequest):
    sekarang = datetime.now(timezone.utc)
    devices[form.id_device] = {
        'waktu_request_terakhir': sekarang,
        'kualitas_rssi_perangkat': form.kualitas_rssi_perangkat,
    }
    return{
        'berhasil': True,
        'timestamp': sekarang
    }

@router.get('/', response_model=list[DeviceResponse], status_code=status.HTTP_200_OK)
def get_data_perangkat():
    sekarang = datetime.now(timezone.utc)
    hasil = []

    for id_device, data_perangkat in devices.items():
        selisih = (
            sekarang - data_perangkat['waktu_request_terakhir']
        ).total_seconds()

        hasil.append({
            'id_device': id_device,
            **data_perangkat,
            'status_perangkat': selisih < MAKSIMUM_WAKTU_DEVICE
        })

    return hasil