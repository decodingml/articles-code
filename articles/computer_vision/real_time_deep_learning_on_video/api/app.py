import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
)
ch.setFormatter(formatter)
logger.addHandler(ch)


def create_fastapi_app():
    app = FastAPI(
        title="video-streaming-api", description="Video streaming API", debug=True
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/info")
    async def info():
        return {"app_name": "video-streaming-api", "app_version": "v1"}

    return app
