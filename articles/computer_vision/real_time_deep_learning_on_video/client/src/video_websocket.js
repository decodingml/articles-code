import React, { useEffect, useState } from 'react';

function WebSocketStream() {
  const [src, setSrc] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8888/ws_video');

    ws.onmessage = (event) => {
      const blob = new Blob([event.data], { type: 'image/jpeg' });
      setSrc(URL.createObjectURL(blob));
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>WebSocket Video Stream</h1>
      <img src={src} alt="Video Stream" style={{ width: "640px", height: "480px" }} />
    </div>
  );
}

export default WebSocketStream;