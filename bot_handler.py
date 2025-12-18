"""
Bot Framework Activity Handler for Event Kit Agent

This module provides the Teams Bot Framework integration for EventKit,
handling incoming activities (messages, reactions, etc.) and routing them
to the appropriate agent functions.

Usage:
    from bot_handler import EventKitBotHandler
    
    handler = EventKitBotHandler()
    response = await handler.on_message_activity(context)
"""

import logging
import json
from typing import Any, Dict, Optional, List
from datetime import datetime

try:
    from botbuilder.core import (
        ActivityHandler,
        ConversationState,
        UserState,
        TurnContext,
        MessageFactory,
        CardFactory,
    )
    from botbuilder.schema import (
        Activity,
        ActivityTypes,
        ChannelAccount,
        Attachment,
        HeroCard,
        CardAction,
        ActionTypes,
        Mention,
    )
    from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
    HAS_BOT_FRAMEWORK = True
except ImportError:
    HAS_BOT_FRAMEWORK = False
    logging.warning("Bot Framework SDK not installed")

# Import Event Kit agent
try:
    from agents_sdk_adapter import EventKitAgent
    from settings import Settings
except ImportError as e:
    logging.warning(f"Failed to import Event Kit modules: {e}")
    EventKitAgent = None
    Settings = None

logger = logging.getLogger(__name__)


class EventKitBotHandler(ActivityHandler if HAS_BOT_FRAMEWORK else object):
    """
    Bot Framework Activity Handler for Event Kit Agent.
    
    This handler processes incoming Teams activities and routes them to
    the appropriate agent functions via the EventKitAgent adapter.
    """
    
    def __init__(
        self,
        conversation_state: Optional[Any] = None,
        user_state: Optional[Any] = None,
        agent: Optional[EventKitAgent] = None,
    ):
        """
        Initialize the bot handler.
        
        Args:
            conversation_state: Conversation state management
            user_state: User state management
            agent: EventKitAgent instance (creates if None)
        """
        if HAS_BOT_FRAMEWORK:
            super().__init__()
        
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.agent = agent or (EventKitAgent() if EventKitAgent else None)
        
        # Message handlers
        self._on_message_activity_handler = self._handle_message
        self._on_message_reaction_activity_handler = self._handle_reaction
        self._on_members_added_activity_handler = self._handle_members_added
        self._on_members_removed_activity_handler = self._handle_members_removed
        
        logger.info("EventKitBotHandler initialized")
    
    async def on_message_activity(self, turn_context: Any) -> None:
        """
        Handle incoming message activity.
        
        Args:
            turn_context: The turn context from Bot Framework
        """
        if not self.agent:
            await turn_context.send_activity(
                MessageFactory.text("Agent is not properly initialized. Please try again.")
            )
            return
        
        try:
            message_text = turn_context.activity.text.strip()
            
            # Parse command and parameters
            command, params = self._parse_message(message_text)
            
            logger.info(f"Processing command: {command} with params: {params}")
            
            # Route to appropriate handler
            if command == "recommend":
                await self._handle_recommend(turn_context, params)
            elif command == "explain":
                await self._handle_explain(turn_context, params)
            elif command == "export":
                await self._handle_export(turn_context, params)
            elif command == "help":
                await self._handle_help(turn_context)
            else:
                # Try as natural language query
                await self._handle_natural_language(turn_context, message_text)
        
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"Error: {str(e)}")
            )
        
        # Save conversation state
        if self.conversation_state:
            await self.conversation_state.save_changes(turn_context)
    
    async def on_message_reaction_activity(self, turn_context: Any) -> None:
        """Handle message reactions."""
        reaction = turn_context.activity.reaction
        logger.info(f"Received reaction: {reaction}")
        await self._handle_reaction(turn_context)
        
        if self.conversation_state:
            await self.conversation_state.save_changes(turn_context)
    
    async def on_members_added_activity(self, members_added: List[Any], turn_context: Any) -> None:
        """Handle members added activity (bot join, user join)."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self._handle_members_added(turn_context, member)
        
        if self.user_state:
            await self.user_state.save_changes(turn_context)
    
    async def on_members_removed_activity(self, members_removed: List[Any], turn_context: Any) -> None:
        """Handle members removed activity."""
        for member in members_removed:
            logger.info(f"Member removed: {member.id}")
        
        if self.user_state:
            await self.user_state.save_changes(turn_context)
    
    # Command handlers
    async def _handle_recommend(self, turn_context: Any, params: Dict[str, str]) -> None:
        """Handle recommend command."""
        interests = params.get("interests", "")
        top = int(params.get("top", "5"))
        
        if not interests:
            await turn_context.send_activity(
                MessageFactory.text(
                    "Please provide interests. Usage: `@bot recommend agents, ai safety --top 3`"
                )
            )
            return
        
        # Show typing indicator
        await turn_context.send_activity(
            Activity(type=ActivityTypes.typing)
        )
        
        try:
            # Call agent
            result = self.agent.handle_tool_call("recommend_sessions", {
                "interests": interests,
                "top": top,
                "correlation_id": turn_context.activity.id
            })
            
            # Create adaptive card with results
            card = self._create_recommendations_card(result)
            await turn_context.send_activity(MessageFactory.attachment(card))
            
            # Send text summary
            summary = f"Found {result['total_count']} recommended sessions based on: {interests}"
            await turn_context.send_activity(MessageFactory.text(summary))
            
        except Exception as e:
            logger.error(f"Error in recommend: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"Error getting recommendations: {str(e)}")
            )
    
    async def _handle_explain(self, turn_context: Any, params: Dict[str, str]) -> None:
        """Handle explain command."""
        session_title = params.get("session", "")
        interests = params.get("interests", "")
        
        if not session_title or not interests:
            await turn_context.send_activity(
                MessageFactory.text(
                    "Usage: `@bot explain \"Session Title\" --interests agents, ai safety`"
                )
            )
            return
        
        # Show typing indicator
        await turn_context.send_activity(
            Activity(type=ActivityTypes.typing)
        )
        
        try:
            result = self.agent.handle_tool_call("explain_session", {
                "session_title": session_title,
                "interests": interests,
                "correlation_id": turn_context.activity.id
            })
            
            # Send explanation as formatted text
            await turn_context.send_activity(
                MessageFactory.text(result['markdown'])
            )
            
        except Exception as e:
            logger.error(f"Error in explain: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"Error: {str(e)}")
            )
    
    async def _handle_export(self, turn_context: Any, params: Dict[str, str]) -> None:
        """Handle export command."""
        interests = params.get("interests", "")
        profile_name = params.get("profile", None)
        
        if not interests:
            await turn_context.send_activity(
                MessageFactory.text(
                    "Usage: `@bot export agents, ai safety --profile my_profile`"
                )
            )
            return
        
        # Show typing indicator
        await turn_context.send_activity(
            Activity(type=ActivityTypes.typing)
        )
        
        try:
            result = self.agent.handle_tool_call("export_itinerary", {
                "interests": interests,
                "profile_name": profile_name,
                "correlation_id": turn_context.activity.id
            })
            
            # Send markdown content
            content = result['markdown']
            
            # If content is too long, send as file
            if len(content) > 4000:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(content)
                    await turn_context.send_activity(
                        MessageFactory.text(f"📄 Itinerary saved ({result['sessions_count']} sessions)")
                    )
            else:
                await turn_context.send_activity(
                    MessageFactory.text(content)
                )
            
            if result['profile_saved']:
                await turn_context.send_activity(
                    MessageFactory.text(f"✅ Profile '{result['profile_name']}' saved!")
                )
        
        except Exception as e:
            logger.error(f"Error in export: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"Error: {str(e)}")
            )
    
    async def _handle_help(self, turn_context: Any) -> None:
        """Handle help command."""
        help_text = """
**Event Kit Agent - Commands**

1. **recommend** - Get session recommendations
   \`@bot recommend agents, ai safety --top 5\`

2. **explain** - Understand why a session matches
   \`@bot explain "Session Title" --interests agents, ai safety\`

3. **export** - Export your personalized itinerary
   \`@bot export agents, machine learning --profile my_profile\`

4. **help** - Show this help message

**Examples:**
- \`recommend ai safety, responsible ai\`
- \`explain "Generative Agents in Production" --interests agents\`
- \`export agents, edge computing\`

Need help? Check the documentation at https://github.com/peterswimm/event-agent-december
"""
        await turn_context.send_activity(MessageFactory.text(help_text))
    
    async def _handle_natural_language(self, turn_context: Any, message: str) -> None:
        """Handle natural language queries."""
        # Simple heuristics to detect intent
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["recommend", "suggest", "find", "session"]):
            # Extract keywords as interests
            interests = self._extract_interests(message)
            if interests:
                params = {"interests": interests, "top": "3"}
                await self._handle_recommend(turn_context, params)
            else:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "I can help find sessions! Try: `recommend agents, ai safety`"
                    )
                )
        else:
            # Generic response
            await turn_context.send_activity(
                MessageFactory.text(
                    "I can help with session recommendations. Type `help` for available commands."
                )
            )
    
    async def _handle_reaction(self, turn_context: Any) -> None:
        """Handle message reactions."""
        reaction = turn_context.activity.reaction
        logger.info(f"Reaction: {reaction}")
    
    async def _handle_members_added(self, turn_context: Any, member: Any) -> None:
        """Handle new member added (greeting)."""
        await turn_context.send_activity(
            MessageFactory.text(
                f"👋 Welcome {member.name}! I'm EventKit Agent. "
                "Type `@bot help` to see what I can do."
            )
        )
    
    async def _handle_members_removed(self, turn_context: Any, member: Any) -> None:
        """Handle member removed."""
        logger.info(f"Member {member.id} removed")
    
    # Utility methods
    def _parse_message(self, message: str) -> tuple[str, Dict[str, str]]:
        """
        Parse message into command and parameters.
        
        Returns:
            Tuple of (command, params_dict)
        """
        parts = message.split()
        if not parts:
            return "help", {}
        
        command = parts[0].lower()
        params = {}
        
        # Simple parameter parsing
        i = 1
        while i < len(parts):
            if parts[i].startswith("--"):
                key = parts[i][2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                    params[key] = parts[i + 1]
                    i += 2
                else:
                    params[key] = "true"
                    i += 1
            else:
                # Treat as positional (interests)
                if "interests" not in params:
                    params["interests"] = " ".join(parts[i:])
                    break
                i += 1
        
        return command, params
    
    def _extract_interests(self, message: str) -> str:
        """Extract interests from natural language message."""
        # Simple extraction: remove common words and use remaining
        stop_words = {"i", "want", "find", "get", "about", "sessions", "for", "session",
                      "recommend", "suggest", "please", "can", "you", "help", "with"}
        
        words = [w.lower().strip(',.!?') for w in message.split()]
        interests = [w for w in words if w not in stop_words and len(w) > 2]
        
        return ", ".join(interests[:3]) if interests else ""
    
    def _create_recommendations_card(self, result: Dict[str, Any]) -> Attachment:
        """Create adaptive card for recommendations."""
        sessions = result.get("sessions", [])[:3]  # Show top 3
        
        card_actions = []
        for session in sessions:
            card_actions.append(
                CardAction(
                    type=ActionTypes.open_url,
                    title=session['title'][:30],
                    value=f"https://eventkit.example.com/session/{session['id']}"
                )
            )
        
        hero_card = HeroCard(
            title="Session Recommendations",
            subtitle=f"Based on your interests ({len(sessions)} results)",
            text=f"Relevance: {', '.join([f\"{s['title'][:25]}...\" for s in sessions])}",
            buttons=card_actions if HAS_BOT_FRAMEWORK else None
        )
        
        if HAS_BOT_FRAMEWORK:
            return CardFactory.hero_card(hero_card)
        else:
            return None


# Convenience functions
def create_bot_handler(
    conversation_state: Optional[Any] = None,
    user_state: Optional[Any] = None,
    agent: Optional[EventKitAgent] = None
) -> EventKitBotHandler:
    """Create and return an EventKitBotHandler instance."""
    return EventKitBotHandler(
        conversation_state=conversation_state,
        user_state=user_state,
        agent=agent
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Bot handler module loaded. Run with bot framework for actual execution.")
