"""
    Core API script. Will mount and append all routers to the API start point.
"""

import uvicorn
from app import create_fastapi_app
from routers import HTTPRouter, WEBRTCRouter, WSRouter

app = create_fastapi_app()
app.include_router(HTTPRouter)
app.include_router(WSRouter)
app.include_router(WEBRTCRouter)


if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", reload=True, port=8000)
