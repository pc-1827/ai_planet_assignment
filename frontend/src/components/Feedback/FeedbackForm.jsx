// src/components/Feedback/FeedbackForm.jsx
import React, { useState } from 'react';
import styled from 'styled-components';
import Button from '../UI/Button';

const FormContainer = styled.div`
  background-color: #f8f9fa;
  border: 1px solid #dadce0;
  border-radius: 8px;
  padding: 16px;
  margin-top: 8px;
`;

const Title = styled.h3`
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 500;
  color: #202124;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 1px solid #dadce0;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-bottom: 12px;
  min-height: 100px;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #4285f4;
    box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
`;

const FeedbackForm = ({ onSubmit, onCancel }) => {
    const [feedback, setFeedback] = useState('');
    const [correction, setCorrection] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(feedback.trim(), correction.trim());
    };

    return (
        <FormContainer>
            <Title>Help improve the solution</Title>

            <form onSubmit={handleSubmit}>
                <div>
                    <TextArea
                        placeholder="What could be improved about this solution?"
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        required
                    />
                </div>

                <div>
                    <TextArea
                        placeholder="Optional: Provide the correct solution or specific corrections"
                        value={correction}
                        onChange={(e) => setCorrection(e.target.value)}
                    />
                </div>

                <ButtonContainer>
                    <Button type="button" onClick={onCancel} color="secondary">
                        Cancel
                    </Button>
                    <Button type="submit" color="primary" disabled={!feedback.trim()}>
                        Submit Feedback
                    </Button>
                </ButtonContainer>
            </form>
        </FormContainer>
    );
};

export default FeedbackForm;