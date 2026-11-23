from fastapi import status, APIRouter, Form, File, Depends
from ..entities.user import User
from .model import (DeteksiRequest, DeteksiResponse, Konfigurasi)
from .service import DeteksiService
from ..core.db import SessionDep
from .model import UploadFile
from ..auth.dependency import require_role, verifikasi_perangkat
router = APIRouter(prefix="/deteksi", tags=['deteksi'])



from fastapi import APIRouter, Request, Depends, Header, HTTPException
from starlette.datastructures import UploadFile
from io import BytesIO
import asyncio

router = APIRouter(prefix="/deteksi", tags=['deteksi'])


import asyncio
import time
from io import BytesIO

from fastapi import Request, Header, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse

temp_batches = {}
batch_lock = asyncio.Lock()

MAX_TOTAL_IMAGE = 10
MAX_IMAGE_SIZE = 5 * 1024 * 1024       # 5 MB
MAX_BATCH_SIZE = 30 * 1024 * 1024      # 30 MB
BATCH_TIMEOUT = 60                     # 60 detik


@router.post("/", response_model=DeteksiResponse, status_code=status.HTTP_200_OK)
async def deteksi_gambar(
    request: Request,
    session: SessionDep,
    _: bool = Depends(verifikasi_perangkat),
    device_id: str = Header(..., alias="X-Device-ID"),
    uid_rfid: str = Header(..., alias="X-UID-RFID"),
    batch_id: str = Header(..., alias="X-Batch-ID"),
    image_index: int = Header(..., alias="X-Image-Index"),
    total_image: int = Header(..., alias="X-Total-Image")
):
    if not 1 <= total_image <= MAX_TOTAL_IMAGE:
        raise HTTPException(400, "TOTAL IMAGE TIDAK VALID")

    if image_index not in range(1, total_image + 1):
        raise HTTPException(400, "INDEX FOTO TIDAK VALID")

    content_type = request.headers.get("content-type", "").split(";")[0]
    if content_type != "image/jpeg":
        raise HTTPException(415, "FORMAT HARUS JPEG")

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_IMAGE_SIZE:
                raise HTTPException(413, "UKURAN FOTO TERLALU BESAR")
        except ValueError:
            raise HTTPException(400, "CONTENT-LENGTH TIDAK VALID")

    # Membaca body dengan batas ukuran
    chunks = []
    size = 0

    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(413, "UKURAN FOTO TERLALU BESAR")
        chunks.append(chunk)

    image_bytes = b"".join(chunks)

    if not image_bytes:
        raise HTTPException(400, "GAMBAR KOSONG")

    now = time.monotonic()

    async with batch_lock:
        # Bersihkan batch kedaluwarsa
        expired_batches = [
            key for key, value in temp_batches.items()
            if now - value["updated_at"] > BATCH_TIMEOUT
        ]

        for key in expired_batches:
            temp_batches.pop(key)

        batch = temp_batches.get(batch_id)

        if batch is None:
            batch = {
                "device_id": device_id,
                "uid_rfid": uid_rfid,
                "total_image": total_image,
                "images": {},
                "total_bytes": 0,
                "started_at": time.perf_counter(),
                "updated_at": now
            }
            temp_batches[batch_id] = batch

        if batch["device_id"] != device_id or batch["uid_rfid"] != uid_rfid:
            raise HTTPException(409, "IDENTITAS BATCH TIDAK SESUAI")

        if batch["total_image"] != total_image:
            raise HTTPException(409, "TOTAL FOTO BATCH TIDAK SESUAI")

        if image_index in batch["images"]:
            raise HTTPException(409, "FOTO SUDAH PERNAH DITERIMA")

        if batch["total_bytes"] + len(image_bytes) > MAX_BATCH_SIZE:
            raise HTTPException(413, "TOTAL UKURAN BATCH TERLALU BESAR")

        batch["images"][image_index] = image_bytes
        batch["total_bytes"] += len(image_bytes)
        batch["updated_at"] = now

        if len(batch["images"]) < total_image:
            return JSONResponse(
                status_code=202,
                content={
                    "status": "waiting",
                    "received": len(batch["images"]),
                    "expected": total_image
                }
            )

        completed_batch = temp_batches.pop(batch_id)

    images = [
        UploadFile(
            filename=f"foto_{i}.jpg",
            file=BytesIO(completed_batch["images"][i])
        )
        for i in range(1, total_image + 1)
    ]

    form = DeteksiRequest(
        device_id=device_id,
        uid_rfid=uid_rfid,
        latensi_request = time.perf_counter() - completed_batch["started_at"]
    )

    servis = DeteksiService(session)
    return await servis.deteksi_gambar(images, form)

@router.get('/', response_model=Konfigurasi, status_code=status.HTTP_200_OK)
def lihat_konfigurasi(session: SessionDep, user: User = Depends(require_role("admin"))):
    servis = DeteksiService(session)
    return servis.lihat_konfigurasi()

@router.patch("/", response_model=Konfigurasi, status_code=status.HTTP_200_OK)
def update_konfigurasi(session: SessionDep,  form: Konfigurasi, user: User = Depends(require_role("admin"))):
    servis = DeteksiService(session)
    return servis.update_konfigurasi(form)


