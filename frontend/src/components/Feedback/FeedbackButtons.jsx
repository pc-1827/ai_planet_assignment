// src/components/Feedback/FeedbackButtons.jsx
import React, { useState } from 'react';
import styled from 'styled-components';
import { useChat } from '../../context/ChatContext';
import FeedbackForm from './FeedbackForm';
import Button from '../UI/Button';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ButtonsContainer = styled.div`
  display: flex;
  gap: 12px;
`;

const FeedbackButtons = ({ messageId, solutionId }) => {
    const { submitFeedback } = useChat();
    const [showFeedbackForm, setShowFeedbackForm] = useState(false);

    const handleCorrect = () => {
        submitFeedback(messageId, solutionId, true);
    };

    const handleIncorrect = () => {
        setShowFeedbackForm(true);
    };

    const handleSubmitFeedback = (feedback, correction) => {
        submitFeedback(messageId, solutionId, false, feedback, correction);
        setShowFeedbackForm(false);
    };

    return (
        <Container>
            <ButtonsContainer>
                <Button
                    onClick={handleCorrect}
                    color="success"
                    icon="✓"
                >
                    Correct
                </Button>
                <Button
                    onClick={handleIncorrect}
                    color="danger"
                    icon="✗"
                >
                    Needs Improvement
                </Button>
            </ButtonsContainer>

            {showFeedbackForm && (
                <FeedbackForm
                    onSubmit={handleSubmitFeedback}
                    onCancel={() => setShowFeedbackForm(false)}
                />
            )}
        </Container>
    );
};

export default FeedbackButtons;