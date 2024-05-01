import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws")
async def ws_video(websocket: WebSocket):
    await websocket.accept()
    video = cv2.VideoCapture("../sample.mp4")

    try:
        while True:
            success, frame = video.read()
            if not success:
                break
            else:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                await websocket.send_bytes(frame_bytes)
    except WebSocketDisconnect as e:
        print(e)
    finally:
        video.release()
        await websocket.close()