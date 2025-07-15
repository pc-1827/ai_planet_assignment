import httpx
import logging
import uuid
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class WebSearchClient:
    """Client for interacting with the open-webSearch MCP server using proper MCP protocol"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/mcp"
        self.session_id = None
    
    async def initialize_session(self) -> bool:
        """Initialize an MCP session with the server"""
        try:
            if self.session_id:
                return True  # Session already initialized
                
            # Create a unique request ID
            request_id = str(uuid.uuid4())
            
            # Initialize MCP session
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "mcp.initialize",
                        "params": {
                            "version": "1.0",
                            "capabilities": {}
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        # Extract session ID from response headers
                        self.session_id = response.headers.get("mcp-session-id")
                        logger.info(f"MCP session initialized with ID: {self.session_id}")
                        return True
                    else:
                        logger.error(f"Failed to initialize MCP session: {result}")
                        return False
                else:
                    logger.error(f"Error initializing MCP session: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error initializing MCP session: {e}")
            return False
    
    async def search(self, query: str, limit: int = 5, engines: List[str] = ["exa"]) -> List[Dict]:
        """
        Search the web using the web search MCP server with proper session handling
        """
        try:
            logger.info(f"Searching web for: {query}")
            
            # Make sure we have a session
            session_initialized = await self.initialize_session()
            if not session_initialized:
                logger.error("Cannot search: MCP session initialization failed")
                return []
            
            # Create a unique request ID
            request_id = str(uuid.uuid4())
            
            # Call the web search MCP server using proper MCP protocol
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers={
                        "Content-Type": "application/json",
                        "mcp-session-id": self.session_id
                    },
                    json={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "mcp.tool.invoke",
                        "params": {
                            "name": "search",
                            "arguments": {
                                "query": query,
                                "limit": limit,
                                "engines": engines
                            }
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Web search response received")
                    if "result" in result:
                        logger.info(f"Found {len(result['result'])} web search results")
                        return result["result"]
                    else:
                        logger.warning(f"Web search returned no results: {result}")
                        return []
                else:
                    logger.error(f"Error from web search API: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []
            
    async def close_session(self):
        """Close the MCP session"""
        if not self.session_id:
            return
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.delete(
                    self.mcp_endpoint,
                    headers={"mcp-session-id": self.session_id}
                )
            logger.info(f"MCP session closed: {self.session_id}")
            self.session_id = None
        except Exception as e:
            logger.error(f"Error closing MCP session: {e}")