import uuid

from aiortc import (
    MediaStreamTrack,
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaPlayer, MediaRelay
from fastapi import APIRouter, Body, FastAPI

app = FastAPI()
router = APIRouter()

relay = MediaRelay()


class VideoStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, source_track):
        super().__init__()
        self.source_track = source_track

    async def recv(self):
        frame = await self.source_track.recv()
        return frame


class RTCConnectionManager:
    def __init__(self):
        self.pc = RTCPeerConnection()

    def create_media_player(self, video_path):
        return MediaPlayer(file=video_path, format="mp4")

    async def handle_offer(self, offer: dict):
        video_track = MediaPlayer(
            file="sample.mp4",
            format="mp4",
        ).video
        relayed_track = relay.subscribe(video_track)
        self.pc.addTrack(VideoStreamTrack(relayed_track))

        self.pc.on(
            "iceconnectionstatechange",
            lambda: print(f"ICE connection state: {self.pc.iceConnectionState}"),
        )
        self.pc.on("track", self.on_track)

        await self.pc.setRemoteDescription(
            RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
        )
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        return {
            "type": "answer",
            "sdp": self.pc.localDescription.sdp,
            "id": offer["id"],
        }

    def on_track(self, track):
        print(f"Track received: {track.kind}")


connection_manager = RTCConnectionManager()


@router.post("/webrtc")
async def webrtc_endpoint(offer: dict = Body(...)):
    offer_id = str(uuid.uuid4())
    offer["id"] = offer_id
    response = await connection_manager.handle_offer(offer)
    return response
