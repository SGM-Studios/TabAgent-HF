"""
Tab Agent Pro - Agents Module
Core audio processing and transcription agents
"""

from .splitter import SplitterAgent
from .ear import EarAgent
from .tab import TabAgent
from .suno_detector import SunoDetector

__all__ = [
    'SplitterAgent',
    'EarAgent', 
    'TabAgent',
    'SunoDetector'
]
