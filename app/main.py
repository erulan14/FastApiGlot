import time

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from .api.api import router as api_router
from .core.config import ALLOWED_HOSTS, API_V1_STR, PROJECT_NAME, DESCRIPTION
from .core.errors import http_422_error_handler, http_error_handler
from app.db.mongodb_utils import close_mongo_connection, connect_to_mongo


app = FastAPI(title=PROJECT_NAME,
              description=DESCRIPTION,
              version="1.0.0",
              terms_of_service="https://glot.kz/terms/",
              contact={
                  "name": "Altynbek Erulan",
                  "url": "https://glot.kz/author/",
                  "email": "erulan@glot.kz"
              },
              swagger_ui_parameters={"defaultModelsExpandDepth": -1})

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(HTTP_422_UNPROCESSABLE_ENTITY, http_422_error_handler)
app.include_router(api_router, prefix=API_V1_STR)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    # async def send_personal_message(self, message: str, websocket: WebSocket):
    #     await websocket.send_text(message)
    #
    # async def broadcast(self, message: str):
    #     for connection in self.active_connections:
    #         await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["Author"] = "Altynbek Erulan"
    return response

