// src/components/UI/Button.jsx
import React from 'react';
import styled, { css } from 'styled-components';

const getButtonColors = (color) => {
    switch (color) {
        case 'primary':
            return css`
        background-color: #4285f4;
        color: white;
        &:hover:not(:disabled) {
          background-color: #3367d6;
        }
      `;
        case 'secondary':
            return css`
        background-color: #f8f9fa;
        color: #3c4043;
        border: 1px solid #dadce0;
        &:hover:not(:disabled) {
          background-color: #f1f3f4;
          box-shadow: 0 1px 2px rgba(60, 64, 67, 0.1);
        }
      `;
        case 'success':
            return css`
        background-color: #34a853;
        color: white;
        &:hover:not(:disabled) {
          background-color: #137333;
        }
      `;
        case 'danger':
            return css`
        background-color: #ea4335;
        color: white;
        &:hover:not(:disabled) {
          background-color: #c5221f;
        }
      `;
        default:
            return css`
        background-color: #4285f4;
        color: white;
        &:hover:not(:disabled) {
          background-color: #3367d6;
        }
      `;
    }
};

const StyledButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${(props) => props.size === 'small' ? '6px 12px' : '8px 16px'};
  border-radius: 4px;
  font-size: ${(props) => props.size === 'small' ? '0.85rem' : '0.9rem'};
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
  border: none;
  
  ${(props) => getButtonColors(props.color)}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.4);
  }
`;

const IconWrapper = styled.span`
  margin-right: 8px;
`;

const Button = ({
    children,
    color = 'primary',
    size = 'medium',
    icon,
    ...props
}) => {
    return (
        <StyledButton color={color} size={size} {...props}>
            {icon && <IconWrapper>{icon}</IconWrapper>}
            {children}
        </StyledButton>
    );
};

export default Button;