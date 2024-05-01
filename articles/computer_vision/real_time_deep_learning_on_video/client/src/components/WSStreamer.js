import React, { useEffect, useState } from 'react';
import { VideoImage, VideoInner, VideoTitle } from './common';

function WebSocketStream() {
  const [src, setSrc] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws');

    ws.onmessage = (event) => {
      const blob = new Blob([event.data], { type: 'image/jpeg' });
      setSrc(URL.createObjectURL(blob));
    };

    return () => ws.close();
  }, []);

  return (
    <VideoInner>
      <VideoTitle>WebSocket Video Stream</VideoTitle>
      <VideoImage src={src} alt="Video Stream" />
    </VideoInner>
  );
}

export default WebSocketStream;
