from sqlmodel import SQLModel, Field


class TabelPengujian(SQLModel):
    __tablename__ = "pengujian"
    #latensi
    latensi_request: float
    latensi_inferensi: float
    latensi_server: float
    latensi_response: float
    latensi_total: float = latensi_request + latensi_response

    #throughput
    