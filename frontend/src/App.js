// src/App.js
import React from 'react';
import { ChatProvider } from './context/ChatContext';
import ChatContainer from './components/Chat/ChatContainer';
import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    padding: 0;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f8f9fa;
    overflow-x: hidden; /* Prevent horizontal scrolling */
  }
  
  html, body, #root {
    height: 100%;
  }
  
  #root {
    display: flex;
    flex-direction: column;
    align-items: center; /* Center the chat container */
    padding: 0; /* Remove padding that might cause scrolling */
  }
`;

function App() {
    return (
        <ChatProvider>
            <GlobalStyle />
            <ChatContainer />
        </ChatProvider>
    );
}

export default App;