import React, { useEffect, useRef } from 'react';

function WebRTCVideo() {
  const videoRef = useRef(null);

  useEffect(() => {
    const pc = new RTCPeerConnection();
    
    const startConnection = async () => {
      try {
        pc.ontrack = event => {
          if (videoRef.current) {
            videoRef.current.srcObject = event.streams[0];
          }
        };
  
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
  
        const response = await fetch('http://localhost:8888/webrtc_offer', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              sdp: pc.localDescription.sdp,
              type: pc.localDescription.type,
            }),
          });
        const data = await response.json();
        await pc.setRemoteDescription(new RTCSessionDescription(data));
      } catch (error) {
        console.error("Error during the WebRTC setup:", error);
        pc.close();
      }
    };
  
    startConnection();
  
    return () => {
      pc.close();
    };
  }, []);

  return (
    <div>
      <h1>Video Stream from Python</h1>
      <video ref={videoRef} playsInline autoPlay />
    </div>
  );
}

export default WebRTCVideo;
