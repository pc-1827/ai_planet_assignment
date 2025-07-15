// src/components/Chat/ChatInput.jsx
import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSend } from 'react-icons/fi';

const InputContainer = styled.div`
  display: flex;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  background-color: white;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #dadce0;
  border-radius: 24px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:focus {
    border-color: #4285f4;
    box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
  }

  &::placeholder {
    color: #9aa0a6;
  }
`;

const SendButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  margin-left: 12px;
  background-color: ${(props) => (props.active ? '#4285f4' : '#e8eaed')};
  color: ${(props) => (props.active ? 'white' : '#9aa0a6')};
  border: none;
  border-radius: 50%;
  cursor: ${(props) => (props.active ? 'pointer' : 'default')};
  transition: background-color 0.2s;

  &:hover {
    background-color: ${(props) => (props.active ? '#3367d6' : '#e8eaed')};
  }
`;

const ChatInput = ({ onSend, disabled }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !disabled) {
            onSend(input.trim());
            setInput('');
        }
    };

    return (
        <InputContainer as="form" onSubmit={handleSubmit}>
            <Input
                type="text"
                placeholder="Ask a mathematics question..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={disabled}
            />
            <SendButton
                type="submit"
                active={input.trim() && !disabled}
                disabled={!input.trim() || disabled}
            >
                <FiSend size={20} />
            </SendButton>
        </InputContainer>
    );
};

export default ChatInput;