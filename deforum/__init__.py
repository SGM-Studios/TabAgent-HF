"""
Deforum Integration - Audio-Reactive Video Generation Module
"""

from .generator import DeforumGenerator
from .audio_sync import AudioSyncEngine
from .presets import STYLE_PRESETS, get_preset, list_presets, get_preset_description

# Type definitions
from .types import (
    AudioFeatures,
    AnimationKeyframe,
    VideoResult,
    StylePreset,
    GenerationConfig,
    MotionParams,
)

__all__ = [
    # Core classes
    'DeforumGenerator',
    'AudioSyncEngine',
    # Presets
    'STYLE_PRESETS',
    'get_preset',
    'list_presets',
    'get_preset_description',
    # Types
    'AudioFeatures',
    'AnimationKeyframe',
    'VideoResult',
    'StylePreset',
    'GenerationConfig',
    'MotionParams',
]
