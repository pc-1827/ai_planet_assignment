import logging
import json
import uuid
import httpx
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Model Context Protocol (MCP) client for communicating with MCP-compliant servers
    """
    
    def __init__(self, server_url: str = "http://localhost:3000/mcp"):
        self.server_url = server_url
        self.session_id = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize an MCP session with the server"""
        if self.initialized and self.session_id:
            return True
            
        try:
            request_id = str(uuid.uuid4())
            
            # Initialize MCP session - no session ID header on initialization
            async with httpx.AsyncClient(timeout=10.0) as client:
                logger.info(f"Initializing MCP session with request ID: {request_id}")
                response = await client.post(
                    self.server_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "mcp.initialize",
                        "params": {
                            "version": "1.0"
                        }
                    }
                )
                
                logger.info(f"Init response status: {response.status_code}")
                
                if response.status_code == 200:
                    # The session ID comes back as a header
                    self.session_id = response.headers.get("mcp-session-id")
                    logger.info(f"Headers received: {response.headers}")
                    
                    if not self.session_id:
                        logger.error("No session ID returned in headers")
                        return False
                        
                    logger.info(f"MCP session initialized with ID: {self.session_id}")
                    self.initialized = True
                    return True
                else:
                    logger.error(f"Failed to initialize MCP session: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error during MCP initialization: {str(e)}")
            return False
    
    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Invoke an MCP tool on the server
        """
        if not self.initialized or not self.session_id:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize MCP session before tool invocation")
                return None
                
        try:
            request_id = str(uuid.uuid4())
            
            # For tool invocation, we MUST include the mcp-session-id header
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Content-Type": "application/json",
                    "mcp-session-id": self.session_id
                }
                
                logger.info(f"Invoking tool '{tool_name}' with session ID: {self.session_id}")
                
                response = await client.post(
                    self.server_url,
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "mcp.tool.invoke",
                        "params": {
                            "name": tool_name,
                            "arguments": arguments
                        }
                    }
                )
                
                # In the invoke_tool method, add this logging to debug the response:
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Tool invocation successful: {tool_name}")
                    logger.info(f"Response content: {result}")  # Add this line
                    if "result" in result:
                        return result["result"]
                    else:
                        logger.warning(f"No result field in response: {result}")
                        return None
                else:
                    logger.error(f"Tool invocation failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error during tool invocation: {str(e)}")
            return None
    
    async def web_search(self, query: str, limit: int = 5, engines: List[str] = ["bing"]) -> List[Dict]:
        """
        Search the web using the MCP web search tool
        """
        logger.info(f"Performing web search for: {query}")
        results = await self.invoke_tool(
            tool_name="search",
            arguments={
                "query": query,
                "limit": limit,
                "engines": engines
            }
        )
        
        if results:
            logger.info(f"Web search returned {len(results)} results")
            return results
        else:
            logger.info("Web search returned no results")
            return []
    
    async def close(self) -> bool:
        """Close the MCP session"""
        if not self.session_id:
            return True
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    self.server_url,
                    headers={"mcp-session-id": self.session_id}
                )
                
            if response.status_code == 200:
                logger.info(f"MCP session closed: {self.session_id}")
                self.session_id = None
                self.initialized = False
                return True
            else:
                logger.error(f"Failed to close MCP session: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error closing MCP session: {str(e)}")
            return False