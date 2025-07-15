// src/context/ChatContext.jsx
import React, { createContext, useState, useContext } from 'react';
import api from '../services/api';

const ChatContext = createContext();

export const useChat = () => useContext(ChatContext);

export const ChatProvider = ({ children }) => {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Add a message to the chat (from user or agent)
    const addMessage = (message) => {
        setMessages((prevMessages) => [...prevMessages, message]);
    };

    // Send a question to the API
    const sendQuestion = async (question) => {
        try {
            setLoading(true);
            setError(null);

            // Add user message
            addMessage({
                id: Date.now(),
                type: 'user',
                content: question,
                timestamp: new Date()
            });

            // Send to API
            const response = await api.sendQuestion(question);

            // Add agent response
            addMessage({
                id: Date.now() + 1,
                type: 'agent',
                content: {
                    solution: response.solution,
                    steps: response.steps,
                    referenceId: response.reference_id
                },
                timestamp: new Date(),
                feedbackGiven: false
            });

            setLoading(false);
            return response;
        } catch (err) {
            setError('Failed to get a response. Please try again.');
            setLoading(false);
            throw err;
        }
    };

    // Submit feedback for a solution
    const submitFeedback = async (messageId, solutionId, isCorrect, feedbackText = null, correction = null) => {
        try {
            setLoading(true);

            // If correct, submit with high rating (5)
            // If incorrect, submit with low rating (2) and include feedback
            const rating = isCorrect ? 5 : 2;

            const response = await api.submitFeedback(
                solutionId,
                rating,
                feedbackText,
                correction
            );

            // Update the message with feedback status
            setMessages(prevMessages =>
                prevMessages.map(msg =>
                    msg.id === messageId
                        ? { ...msg, feedbackGiven: true, feedbackWasPositive: isCorrect }
                        : msg
                )
            );

            setLoading(false);

            // If we got an improved solution back
            if (!isCorrect && response.improved_solution) {
                addMessage({
                    id: Date.now(),
                    type: 'agent',
                    content: {
                        solution: response.improved_solution.solution,
                        steps: response.improved_solution.steps,
                        referenceId: response.improved_solution.reference_id,
                        isImproved: true
                    },
                    timestamp: new Date(),
                    feedbackGiven: false
                });
            }

            return response;
        } catch (err) {
            setError('Failed to submit feedback. Please try again.');
            setLoading(false);
            throw err;
        }
    };

    const value = {
        messages,
        loading,
        error,
        sendQuestion,
        submitFeedback
    };

    return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};