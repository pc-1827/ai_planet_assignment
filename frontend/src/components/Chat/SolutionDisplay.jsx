// src/components/Chat/SolutionDisplay.jsx
import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import 'katex/dist/katex.min.css';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const SolutionContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SolutionHeader = styled.div`
  font-weight: 600;
  font-size: 1.1rem;
  color: #202124;
  margin-bottom: 4px;
`;

const SolutionContent = styled.div`
  margin-bottom: 16px;
  line-height: 1.5;
`;

const StepsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const StepsHeader = styled.div`
  font-weight: 600;
  color: #202124;
  margin-bottom: 4px;
`;

const StepItem = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-start;
`;

const StepNumber = styled.div`
  background-color: #e8eaed;
  color: #5f6368;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 500;
  flex-shrink: 0;
`;

const StepContent = styled.div`
  flex: 1;
  line-height: 1.5;
`;

const MarkdownContent = ({ content }) => (
    <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
    >
        {content}
    </ReactMarkdown>
);

const SolutionDisplay = ({ solution, steps }) => {
    // Check if this appears to be an error message or no-solution case
    const isSolutionError =
        solution.includes("I couldn't generate") ||
        solution.includes("Unable to generate") ||
        solution.includes("I can only help with mathematics");

    return (
        <SolutionContainer>
            <div>
                <SolutionHeader>Solution:</SolutionHeader>
                <SolutionContent>
                    <MarkdownContent content={solution} />
                </SolutionContent>
            </div>

            {/* Only display steps if solution is valid and steps exist */}
            {!isSolutionError && steps && steps.length > 0 && (
                <div>
                    <StepsHeader>Steps:</StepsHeader>
                    <StepsContainer>
                        {steps.map((step, index) => (
                            <StepItem key={index}>
                                <StepNumber>{index + 1}</StepNumber>
                                <StepContent>
                                    <MarkdownContent content={step} />
                                </StepContent>
                            </StepItem>
                        ))}
                    </StepsContainer>
                </div>
            )}
        </SolutionContainer>
    );
};

export default SolutionDisplay;