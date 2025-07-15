// src/components/UI/Spinner.jsx
import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const bounce = keyframes`
  0%, 100% { transform: scale(0.5); }
  50% { transform: scale(1.0); }
`;

const SpinnerContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

const SpinnerDot = styled.div`
  width: ${(props) => (props.size === 'small' ? '6px' : '10px')};
  height: ${(props) => (props.size === 'small' ? '6px' : '10px')};
  background-color: ${(props) => props.color || '#4285f4'};
  border-radius: 50%;
  animation: ${bounce} 1.2s infinite ease-in-out;
  animation-delay: ${(props) => props.delay}s;
`;

const Spinner = ({ size = 'medium', color }) => {
    return (
        <SpinnerContainer>
            <SpinnerDot size={size} color={color} delay={0} />
            <SpinnerDot size={size} color={color} delay={0.2} />
            <SpinnerDot size={size} color={color} delay={0.4} />
        </SpinnerContainer>
    );
};

export default Spinner;