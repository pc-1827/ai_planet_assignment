// src/services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = {
    // Send a question to the Math Professor Agent
    async sendQuestion(question) {
        try {
            const response = await axios.post(`${API_URL}/solve`, { question });
            return response.data;
        } catch (error) {
            console.error('Error sending question:', error);
            throw error;
        }
    },

    // Submit feedback for a solution
    async submitFeedback(solutionId, rating, feedbackText = null, correction = null) {
        try {
            const response = await axios.post(`${API_URL}/feedback`, {
                solution_id: solutionId,
                rating,
                feedback_text: feedbackText,
                correction
            });
            return response.data;
        } catch (error) {
            console.error('Error submitting feedback:', error);
            throw error;
        }
    }
};

export default api;