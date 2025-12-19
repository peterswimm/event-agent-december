"""
Talk-Specific Knowledge Schema

Extends BaseKnowledgeArtifact with research talk/transcript-specific fields.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class TalkSection:
    """Section of a talk with timing information"""
    title: str
    start_minute: int
    duration_minutes: int
    description: Optional[str] = None


@dataclass
class TalkKnowledgeArtifact:
    """Extended knowledge artifact for research talks and transcripts"""

    # Talk metadata
    talk_type: str = "research_update"  # research_update|keynote|demo|tutorial|other
    duration_minutes: Optional[int] = None

    # Structure
    section_breakdown: List[TalkSection] = field(default_factory=list)

    # Demonstrations
    demo_included: bool = False
    demo_description: Optional[str] = None
    demo_type: Optional[str] = None  # "live", "recorded", "simulated"

    # Content analysis
    experimental_results_discussed: bool = False
    technical_challenges_mentioned: List[str] = field(default_factory=list)
    risks_discussed: List[str] = field(default_factory=list)

    # Future direction
    pending_experiments: List[str] = field(default_factory=list)
    collaboration_requests: Optional[str] = None

    # Audience context
    intended_audience: str = "technical"  # technical|general|mixed
    technical_depth_level: str = "intermediate"  # introductory|intermediate|advanced
    assumed_background: Optional[str] = None

    # Engagement signals
    off_script_insights: Optional[str] = None  # Speaker asides and elaborations
    implicit_assumptions: List[str] = field(default_factory=list)
    audience_qa_signals: Optional[str] = None  # What questions revealed about understanding
    strategic_hints: Optional[str] = None  # Hints about commercialization, roadmap, etc.

    # Confidence markers
    speaker_confidence_markers: Optional[str] = None  # Hedging language, uncertainty indicators
