import React from 'react';
import { VideoImage, VideoInner, VideoTitle } from './common';

function HTTPStream() {
  return (
    <VideoInner>
      <VideoTitle>HTTP Video Stream</VideoTitle>
      <VideoImage src="http://127.0.0.1:8000/http" alt="Video Stream" />
    </VideoInner>
  );
}

export default HTTPStream;
