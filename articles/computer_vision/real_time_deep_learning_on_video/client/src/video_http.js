import React from 'react';

function HTTPStream() {
  return (
    <div style={{ textAlign: 'center' }}>
      <h1>HTTP Video Stream</h1>
      <img src="http://localhost:8000/http_video" alt="Video Stream" style={{ width: "640px", height: "480px" }} />
    </div>
  );
}

export default HTTPStream;