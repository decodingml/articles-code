import axios from 'axios';
import React, { useEffect, useRef } from 'react';


function WebRTCVideo() {
  const videoRef = useRef(null);

  const negotiate = async (pc) => {
    pc.addTransceiver('video', { direction: 'recvonly' });
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    await new Promise((resolve) => {
      if (pc.iceGatheringState === 'complete') {
        resolve();
      } else {
        const checkState = () => {
          if (pc.iceGatheringState === 'complete') {
            pc.removeEventListener('icegatheringstatechange', checkState);
            resolve();
          }
        };
        pc.addEventListener('icegatheringstatechange', checkState);
      }
    });

    try {
      const response = await axios.post("http://127.0.0.1:8000/webrtc", {
        sdp: pc.localDescription.sdp,
        type: pc.localDescription.type
      });

      if (response.status === 200 && response.data.sdp && response.data.type) {
        await pc.setRemoteDescription(new RTCSessionDescription(response.data));
      } else {
        throw new Error('Failed to receive valid SDP data from server');
      }
    } catch (error) {
      console.error('Error during SDP exchange:', error);
      throw error;
    }
  };

  useEffect(() => {
    const pc = new RTCPeerConnection();

    pc.ontrack = (evt) => {
      console.log('Received track:', evt.track);
      if (evt.track.kind === 'video') {
        videoRef.current.srcObject = evt.streams[0];
      }
    };

    pc.onicecandidate = event => {
      console.log('ICE Candidate:', event.candidate);
      if (!event.candidate) {
        console.log('ICE Gathering State Complete:', pc.iceGatheringState);
      }
    };
    
    pc.oniceconnectionstatechange = () => {
      console.error('ICE Connection State Change:', pc.iceConnectionState);
      if (pc.iceConnectionState === 'failed') {
        console.error('ICE Connection State is failed, checking for potential recovery');
      }
    };

    negotiate(pc).catch(error => console.error('Failed to negotiate:', error));

    return () => {
      pc.close();
    };
  }, []);

  return (
    <div>
      <h3>Video Stream from Python</h3>
      <video ref={videoRef} autoPlay playsInline muted />
    </div>
  );
}

export default WebRTCVideo;
