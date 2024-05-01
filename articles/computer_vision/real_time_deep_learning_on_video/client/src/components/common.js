import styled from 'styled-components';

export const MainContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
`;

export const VideoContainer = styled.div`
  width: 80%;
  max-width: 640px; 
  aspect-ratio: 16 / 9; 
  background-color: #000; 
  border-radius: 20px; 
  overflow: hidden; 
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
`;

export const ButtonRow = styled.div`
  display: flex;
  gap: 10px;
`;

export const VideoInner = styled.div`
  text-align: center;
`;

export const VideoTitle = styled.h3``;

export const Video = styled.video`
  width: 640px;
  height: 480px;
`;

export const VideoImage = styled.img`
width: 640px;
height: 480px;
`;


export const StyledButton = styled.button`
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  background-color: #007BFF;
  color: white;
  transition: background-color 0.3s, transform 0.2s;

  &:hover {
    background-color: #0056b3;
    transform: scale(1.1);
  }

  &:focus {
    outline: none;
  }
`;