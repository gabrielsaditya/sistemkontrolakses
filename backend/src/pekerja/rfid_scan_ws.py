from fastapi import WebSocket

class ScanRfidOnly:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def hubungkan(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)

    def putus_koneksi(self, websocket: WebSocket):
        if websocket in self.clients:
            self.clients.remove(websocket)

    async def broadcast(self, data: dict):
        for client in self.clients.copy():
            try:
                await client.send_json(data)
            except Exception:
                self.putus_koneksi(client)


scan_rfid_only = ScanRfidOnly()


