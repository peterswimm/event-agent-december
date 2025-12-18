#!/usr/bin/env python3
"""
Bot Framework Server for Event Kit Agent

This module hosts the EventKit agent using aiohttp and handles Teams/Bot Framework activities.

Usage:
    python bot_server.py
    
Environment Variables:
    PORT: Server port (default: 3978)
    BOT_ID: Bot application ID
    BOT_PASSWORD: Bot application password
"""

import os
import sys
import logging
import asyncio
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import dependencies
try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    logger.warning("aiohttp not installed. Install with: pip install aiohttp")

try:
    from botbuilder.core import ConversationState, MemoryStorage, UserState
    from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
    HAS_BOT_FRAMEWORK = True
except ImportError:
    HAS_BOT_FRAMEWORK = False
    logger.warning("Bot Framework SDK not installed. Install with: pip install botbuilder-core botbuilder-integration-aiohttp")

# Import EventKit components
try:
    from bot_handler import EventKitBotHandler
    from agents_sdk_adapter import EventKitAgent
    HAS_EVENTKIT = True
except ImportError as e:
    HAS_EVENTKIT = False
    logger.warning(f"EventKit components not available: {e}")


class EventKitBotServer:
    """Bot Framework server for Event Kit Agent."""
    
    def __init__(self, port: int = 3978):
        """Initialize bot server."""
        self.port = port
        self.adapter: Optional[CloudAdapter] = None
        self.bot_handler: Optional[EventKitBotHandler] = None
        self.memory = MemoryStorage() if HAS_BOT_FRAMEWORK else None
        self.conversation_state = None
        self.user_state = None
    
    async def initialize(self) -> None:
        """Initialize server components."""
        if not HAS_BOT_FRAMEWORK:
            raise RuntimeError("Bot Framework SDK not installed")
        
        if not HAS_EVENTKIT:
            raise RuntimeError("EventKit components not available")
        
        # Initialize storage
        self.memory = MemoryStorage()
        self.conversation_state = ConversationState(self.memory)
        self.user_state = UserState(self.memory)
        
        # Initialize bot handler
        agent = EventKitAgent()
        self.bot_handler = EventKitBotHandler(
            conversation_state=self.conversation_state,
            user_state=self.user_state,
            agent=agent
        )
        
        # Initialize adapter
        auth = ConfigurationBotFrameworkAuthentication()
        self.adapter = CloudAdapter(auth)
        
        # Set up error handler
        async def on_adapter_error(context, error):
            logger.exception(f"Adapter error: {error}")
            await context.send_activity(f"Error: {str(error)}")
        
        self.adapter.on_turn_error = on_adapter_error
        
        logger.info("Bot server initialized successfully")
    
    async def handle_messages(self, req: web.Request) -> web.Response:
        """Handle incoming Bot Framework activities."""
        try:
            body = await req.json()
            auth_header = req.headers.get("Authorization", "")
            
            logger.debug(f"Received activity: {body.get('type', 'unknown')}")
            
            response = await self.adapter.process_activity(
                auth_header,
                body,
                self.bot_handler.on_turn
            )
            
            if response:
                return web.json_response(data=response.body)
            else:
                return web.Response(status=201)
        
        except Exception as e:
            logger.exception(f"Error handling message: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def handle_health(self, req: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "ok",
            "service": "EventKit Bot",
            "port": self.port
        })
    
    async def create_app(self) -> web.Application:
        """Create and configure aiohttp application."""
        app = web.Application()
        
        # Routes
        app.router.add_post("/api/messages", self.handle_messages)
        app.router.add_get("/health", self.handle_health)
        app.router.add_get("/", self.handle_health)
        
        # Graceful shutdown
        async def on_startup():
            logger.info(f"EventKit Bot Server starting on port {self.port}")
            await self.initialize()
        
        async def on_cleanup():
            logger.info("EventKit Bot Server shutting down")
        
        app.on_startup.append(on_startup)
        app.on_cleanup.append(on_cleanup)
        
        return app
    
    def run(self) -> None:
        """Start the bot server."""
        if not HAS_AIOHTTP:
            logger.error("aiohttp is required. Install with: pip install aiohttp")
            sys.exit(1)
        
        if not HAS_BOT_FRAMEWORK:
            logger.error("Bot Framework SDK is required. Install with: pip install botbuilder-core botbuilder-integration-aiohttp")
            sys.exit(1)
        
        try:
            loop = asyncio.get_event_loop()
            app = loop.run_until_complete(self.create_app())
            
            logger.info(f"Starting EventKit Bot Server on 0.0.0.0:{self.port}")
            logger.info(f"Messages endpoint: http://0.0.0.0:{self.port}/api/messages")
            logger.info(f"Health check: http://0.0.0.0:{self.port}/health")
            
            web.run_app(app, host="0.0.0.0", port=self.port, print=logger.info)
        
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.exception(f"Failed to start server: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    port = int(os.getenv("PORT", "3978"))
    server = EventKitBotServer(port=port)
    server.run()


if __name__ == "__main__":
    main()
