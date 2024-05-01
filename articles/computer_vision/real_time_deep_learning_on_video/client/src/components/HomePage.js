import React, { useState } from 'react';
import HTTPStream from './HTTPStreamer';
import WebRTCVideo from './WEBRTCStreamer';
import WebSocketStream from './WSStreamer';
import { ButtonRow, MainContainer, StyledButton, VideoContainer } from './common';

const HomePage = () => {
  const [streamType, setStreamType] = useState('');

  const renderStream = () => {
    switch (streamType) {
      case 'http':
        return <HTTPStream />;
      case 'ws':
        return <WebSocketStream />;
      case 'webrtc':
        return <WebRTCVideo />;
      default:
        return <div>Select a stream type.</div>;
    }
  };

  return (
    <MainContainer>
      <VideoContainer>
        {renderStream()}
      </VideoContainer>
      <ButtonRow>
        <StyledButton onClick={() => setStreamType('http')}>HTTP Stream</StyledButton>
        <StyledButton onClick={() => setStreamType('ws')}>WebSocket Stream</StyledButton>
        <StyledButton onClick={() => setStreamType('webrtc')}>WebRTC Stream</StyledButton>
      </ButtonRow>
    </MainContainer>
  );
}

export default HomePage;