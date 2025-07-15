// src/components/Chat/Message.jsx
import React from 'react';
import styled from 'styled-components';
import SolutionDisplay from './SolutionDisplay';
import FeedbackButtons from '../Feedback/FeedbackButtons';
import { formatDistanceToNow } from 'date-fns';

const MessageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 85%;
  align-self: ${(props) => (props.isUser ? 'flex-end' : 'flex-start')};
`;

const MessageBubble = styled.div`
  padding: ${(props) => (props.isUser ? '12px 18px' : '16px 20px')};
  background-color: ${(props) => (props.isUser ? '#4285f4' : 'white')};
  color: ${(props) => (props.isUser ? 'white' : '#202124')};
  border-radius: 18px;
  border: ${(props) => (props.isUser ? 'none' : '1px solid #e0e0e0')};
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-size: 1rem;
  line-height: 1.5;
  overflow-wrap: break-word;
`;

const UserMessageContent = styled.p`
  margin: 0;
`;

const Timestamp = styled.div`
  font-size: 0.75rem;
  color: #70757a;
  margin-top: 4px;
  align-self: ${(props) => (props.isUser ? 'flex-end' : 'flex-start')};
`;

const FeedbackContainer = styled.div`
  margin-top: 12px;
`;

const FeedbackGiven = styled.div`
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  background-color: ${(props) => (props.isPositive ? '#e6f4ea' : '#fce8e6')};
  color: ${(props) => (props.isPositive ? '#137333' : '#c5221f')};
`;

const ImprovedSolutionBadge = styled.div`
  background-color: #e8f0fe;
  color: #1967d2;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 8px;
  display: inline-block;
`;

const Message = ({ message }) => {
    const isUser = message.type === 'user';
    const timeAgo = formatDistanceToNow(new Date(message.timestamp), { addSuffix: true });

    return (
        <MessageWrapper isUser={isUser}>
            {isUser ? (
                <MessageBubble isUser={true}>
                    <UserMessageContent>{message.content}</UserMessageContent>
                </MessageBubble>
            ) : (
                <>
                    {message.content.isImproved && (
                        <ImprovedSolutionBadge>Improved Solution</ImprovedSolutionBadge>
                    )}
                    <MessageBubble isUser={false}>
                        <SolutionDisplay
                            solution={message.content.solution}
                            steps={message.content.steps}
                        />
                    </MessageBubble>

                    {!message.feedbackGiven ? (
                        <FeedbackContainer>
                            <FeedbackButtons
                                messageId={message.id}
                                solutionId={message.content.referenceId}
                            />
                        </FeedbackContainer>
                    ) : (
                        <FeedbackGiven isPositive={message.feedbackWasPositive}>
                            {message.feedbackWasPositive
                                ? "Thanks for confirming! This solution has been saved for future reference."
                                : "Thanks for your feedback! An improved solution has been provided."}
                        </FeedbackGiven>
                    )}
                </>
            )}
            <Timestamp isUser={isUser}>{timeAgo}</Timestamp>
        </MessageWrapper>
    );
};

export default Message;