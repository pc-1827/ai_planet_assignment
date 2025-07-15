# Math Professor Agent

A sophisticated AI-powered mathematical assistant with step-by-step problem-solving, web search capabilities, and human feedback integration.

## Overview

The Math Professor Agent is an AI-powered system designed to help users solve mathematical problems with detailed step-by-step explanations. The agent uses a combination of vector-based knowledge retrieval, web search capabilities via the Model Context Protocol (MCP), and a human feedback system to continuously improve its responses.

![Math Professor Agent Architecture](https://mermaid.ink/img/pako:eNqFkc9qwzAMxl_F-LRB83dZT4XCYKPsELZDL0GxlcbU-YPtlJXSd5-SrmEbZTuJ7-en70PKQAY1CgzfrbSGvxRpRw5FSRB0oIYfwkB9pUq2tB8VE1gqmLUg2yiQlS7aWKdqeOO7VBqF8vd-qZ56Oe_lYh8lIXOFNJuDpY-wTVTxFPUjdytcCTLJHJTXWi7_0JVIkkRIjg-Wo2QQWdwsRqvF9fUpGXmF8sLrGvqbg3ZIhcQB4-h8nO20bFAr3x-e9uO11JRPPJsORjOwXqYj7AzPkr9Zrb77tmLwCqp3cNZTGgN6DFg9AJNn3WKJF5e6-C2aPlNbFDSYNNCt1AEa_A-xt6KkC9qEEO9-fPxLFQMPz4KF-5KfaRGnj1Z-8-svrMy0dw?type=png)

## Key Features

- **Mathematical Problem-Solving**: Provides detailed, step-by-step solutions to a wide range of mathematical problems
- **Vector Database**: Stores previously solved problems for quick retrieval
- **Web Search Integration**: Uses Exa API to search the internet for solutions to novel problems
- **Input & Output Guardrails**: Ensures only math-related questions are processed and solutions are high-quality
- **Human-in-the-Loop Feedback**: Allows users to provide feedback and corrections to improve future responses

## Prerequisites

Before setting up the Math Professor Agent, ensure you have the following installed:

- **Python 3.9+**
- **Node.js 18+**
- **Docker** (for running Qdrant vector database)
- **npm** (for frontend and MCP server dependencies)

## Getting Started

Follow these comprehensive steps to set up and run the Math Professor Agent:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai_planet_assignment
```

### 2. Set Up Backend

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Qdrant Vector Database

```bash
# Pull and start Qdrant container
docker pull qdrant/qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_data:/qdrant/storage \
    --name qdrant qdrant/qdrant

# Verify Qdrant is running
curl http://localhost:6333/healthz
```

### 4. Load the Dataset into Qdrant

```bash
# First download the dataset if needed
mkdir -p data
# Download your math dataset files to the data directory

# Run the dataset loading script
python scripts/load_dataset.py
```

The load_dataset.py script should:
1. Process your mathematical problem dataset
2. Generate embeddings for each problem
3. Upload the problems and embeddings to Qdrant
4. Create appropriate collections and indices

### 5. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=math_problems

# Exa API Key (Get from https://exa.ai)
EXA_API_KEY=your_exa_api_key_here

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3
```

### 6. Set Up MCP Server

```bash
# Navigate to MCP directory
cd mcp

# Install dependencies
npm install

# Set your Exa API key in the environment
export EXA_API_KEY=your_exa_api_key_here  # On Windows: set EXA_API_KEY=your_exa_api_key_here

# Start the MCP server
node mcp-server.js
```

The MCP server will run on port 3000 and provide web search capabilities.

### 7. Set Up Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The React frontend will run on port 3001.

### 8. Start the FastAPI Backend

```bash
# From the project root directory
cd app
python -m uvicorn main:app --reload
```

The FastAPI backend will run on port 8000.

## Usage

Once all components are running, open your browser to http://localhost:3001 to access the Math Professor Chat interface.

### Example Questions from Knowledge Base

Try these questions which are stored in our vector database:

1. **Algebra**: "Solve the quadratic equation x^2 - 4x + 4 = 0 using the quadratic formula."
2. **Calculus**: "Find the derivative of f(x) = x^3 - 3x^2 + 2x - 1."
3. **Geometry**: "Calculate the volume of a sphere with radius 5 cm."

### Example Questions for Web Search

Try these questions that require web search:

1. "What is the formula for the volume of a truncated cone?"
2. "Explain how to use L'Hôpital's rule with an example."
3. "Solve the system of equations using Cramer's rule: 3x + 2y = 7, 5x - y = 8."

## Project Structure

```
ai_planet_assignment/
│
├── app/                    # FastAPI backend
│   ├── agent/              # LangGraph agent components
│   ├── __init__.py
│   ├── feedback_store.py   # Human feedback storage
│   ├── guardrails.py       # Input/output validation
│   ├── llm_service.py      # LLM integration
│   ├── main.py             # FastAPI main application
│   ├── mcp_client.py       # Client for MCP server
│   ├── models.py           # Pydantic data models
│   ├── vector_store.py     # Qdrant client
│   └── web_search_client.py # Web search interface
│
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── context/        # React context
│   │   ├── services/       # API services
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
│
├── mcp/                    # MCP server for web search
│   ├── mcp-server.js       # Express.js server with Exa
│   └── package.json
│
├── scripts/                # Utility scripts
│   └── load_dataset.py     # Script to load data into Qdrant
│
├── data/                   # Dataset directory
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .env                    # Environment variables
```

## Troubleshooting

### Common Issues

1. **Qdrant Connection Error**:
   - Ensure Docker is running
   - Check if the Qdrant container is active: `docker ps`
   - Restart the container if needed: `docker restart qdrant`

2. **MCP Server Issues**:
   - Verify your Exa API key is correctly set
   - Check the console for error messages
   - Ensure port 3000 is not in use by another application

3. **Frontend-Backend Connection**:
   - Check that CORS is properly configured in the FastAPI app
   - Verify that the API URL in the frontend matches your backend URL

4. **LLM Integration Issues**:
   - Ensure Ollama is installed and running (if using locally)
   - Verify the model is available: `ollama list`
