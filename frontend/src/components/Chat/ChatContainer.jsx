// src/components/Chat/ChatContainer.jsx
import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useChat } from '../../context/ChatContext';
import Message from './Message';
import ChatInput from './ChatInput';
import Spinner from '../UI/Spinner';

const ChatContainerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: auto;  /* Changed from 100vh to auto */
  min-height: 750px;  /* Minimum reasonable height */
  max-height: 150vh;   /* Don't let it get too tall */
  min-width: 1500px;
  margin: 0 2;
  background-color: #f5f7fb;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const Header = styled.div`
  background-color: #4285f4;
  color: white;
  padding: 16px 20px;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
`;

const MathIcon = styled.span`
  margin-right: 10px;
  font-size: 1.5rem;
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(90vh - 140px); /* Account for header and input */
`;

const LoadingIndicator = styled.div`
  display: flex;
  justify-content: center;
  padding: 20px;
`;

const ErrorMessage = styled.div`
  background-color: #ffebee;
  color: #d32f2f;
  padding: 10px 16px;
  border-radius: 8px;
  margin: 10px 0;
  text-align: center;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9aa0a6;
  text-align: center;
  padding: 0 20px;
`;

const EmptyStateTitle = styled.h2`
  margin-bottom: 10px;
  font-weight: 500;
`;

const EmptyStateText = styled.p`
  max-width: 500px;
  line-height: 1.5;
`;

const ChatContainer = () => {
    const { messages, loading, error, sendQuestion } = useChat();
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        if (messagesEndRef.current) {
            // Use scrollIntoView with a slight delay to ensure proper rendering
            setTimeout(() => {
                messagesEndRef.current.scrollIntoView({
                    behavior: 'smooth',
                    block: 'end'
                });
            }, 100);
        }
    }, [messages]);

    return (
        <ChatContainerWrapper>
            <Header>
                <MathIcon>∑</MathIcon>
                Math Professor Chat
            </Header>

            <MessagesContainer>
                {messages.length === 0 ? (
                    <EmptyState>
                        <EmptyStateTitle>Welcome to Math Professor Chat!</EmptyStateTitle>
                        <EmptyStateText>
                            Ask any mathematics question and I'll provide a step-by-step solution.
                            Try questions about algebra, calculus, geometry, or any other math topic.
                        </EmptyStateText>
                    </EmptyState>
                ) : (
                    messages.map((message) => (
                        <Message key={message.id} message={message} />
                    ))
                )}

                {loading && (
                    <LoadingIndicator>
                        <Spinner />
                    </LoadingIndicator>
                )}

                {error && <ErrorMessage>{error}</ErrorMessage>}

                <div ref={messagesEndRef} />
            </MessagesContainer>

            <ChatInput onSend={sendQuestion} disabled={loading} />
        </ChatContainerWrapper>
    );
};

export default ChatContainer;