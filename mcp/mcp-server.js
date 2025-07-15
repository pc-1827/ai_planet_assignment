const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const Exa = require('exa-js').default;

const EXA_API_KEY = process.env.EXA_API_KEY || "your_exa_api_key_here";
const exa = new Exa(EXA_API_KEY);

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

const sessions = {};

async function performExaSearch(query, limit = 5) {
    try {
        console.log(`Performing Exa search for: "${query}"`);

        const searchQuery = query.includes("math problem") ?
            query :
            `math problem solution: ${query}`;

        const searchResults = await exa.searchAndContents(
            searchQuery,
            {
                numResults: limit,
                text: true
            }
        );

        console.log(`Exa search returned ${searchResults.results.length} results`);

        return searchResults.results.map(result => ({
            title: result.title || result.url,
            url: result.url,
            description: result.text || result.snippet || "No description available",
            source: "Exa",
            engine: "exa"
        }));
    } catch (error) {
        console.error(`Error during Exa search: ${error.message}`);
    }
}

app.post('/mcp', async (req, res) => {
    const { method, params, id } = req.body;
    const sessionId = req.headers['mcp-session-id'];

    console.log(`Received request: ${method}, session: ${sessionId || 'none'}`);

    if (method === 'mcp.initialize' && !sessionId) {
        const newSessionId = uuidv4();
        sessions[newSessionId] = {
            id: newSessionId,
            createdAt: new Date(),
            lastAccessed: new Date()
        };

        console.log(`Created new session: ${newSessionId}`);

        res.setHeader('mcp-session-id', newSessionId);
        res.json({
            jsonrpc: '2.0',
            result: {
                version: '1.0',
                capabilities: {
                    tools: ['search']
                }
            },
            id
        });
        return;
    }

    if (sessionId && sessions[sessionId]) {
        sessions[sessionId].lastAccessed = new Date();

        if (method === 'mcp.tool.invoke') {
            const { name, arguments: args } = params;

            if (name === 'search') {
                try {
                    const query = args.query || '';
                    const limit = args.limit || 3;

                    console.log(`Performing search: "${query}", limit ${limit}`);

                    const results = await performExaSearch(query, limit);

                    console.log(`Returning ${results.length} search results`);

                    res.json({
                        jsonrpc: '2.0',
                        result: results,
                        id
                    });
                    return;
                } catch (error) {
                    console.error('Search error:', error);
                    res.status(500).json({
                        jsonrpc: '2.0',
                        error: {
                            code: -32000,
                            message: `Search failed: ${error.message}`
                        },
                        id
                    });
                    return;
                }
            }

            res.status(400).json({
                jsonrpc: '2.0',
                error: {
                    code: -32601,
                    message: `Unknown tool: ${name}`
                },
                id
            });
            return;
        }

        res.status(400).json({
            jsonrpc: '2.0',
            error: {
                code: -32601,
                message: `Unknown method: ${method}`
            },
            id
        });
        return;
    }

    res.status(400).json({
        jsonrpc: '2.0',
        error: {
            code: -32000,
            message: 'Bad Request: No valid session ID provided'
        },
        id: null
    });
});

app.delete('/mcp', (req, res) => {
    const sessionId = req.headers['mcp-session-id'];

    if (sessionId && sessions[sessionId]) {
        delete sessions[sessionId];
        console.log(`Closed session: ${sessionId}`);
        res.status(200).send();
    } else {
        res.status(400).json({
            jsonrpc: '2.0',
            error: {
                code: -32000,
                message: 'Invalid session ID'
            },
            id: null
        });
    }
});

app.listen(PORT, () => {
    console.log(`MCP server running on port ${PORT}`);
    console.log(`Server is ready to handle MCP requests`);
    console.log(`Using Exa search API for web search requests`);
});