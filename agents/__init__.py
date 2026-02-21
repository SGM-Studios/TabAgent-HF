"""
Tab Agent Pro - Agents Module
Core audio processing and transcription agents
"""

from .splitter import SplitterAgent
from .ear import EarAgent
from .tab import TabAgent
from .suno_detector import SunoDetector

# Type definitions
from .types import (
    Note,
    TabNote,
    AudioAnalysis,
    Tuning,
    Instrument,
    Technique,
    STANDARD_TUNINGS,
    get_tuning,
)

# Exceptions
from .exceptions import (
    TabAgentError,
    AudioProcessingError,
    TranscriptionError,
    ModelLoadError,
    StemSeparationError,
    TabGenerationError,
    InvalidAudioError,
    InvalidTuningError,
    UnplayableNoteError,
)

# Utilities
from .utils import (
    detect_device,
    validate_audio_path,
    normalize_audio,
    midi_to_note_name,
    note_name_to_midi,
    format_time,
    ensure_directory,
    get_instrument_range,
)

__all__ = [
    # Agents
    'SplitterAgent',
    'EarAgent',
    'TabAgent',
    'SunoDetector',
    # Types
    'Note',
    'TabNote',
    'AudioAnalysis',
    'Tuning',
    'Instrument',
    'Technique',
    'STANDARD_TUNINGS',
    'get_tuning',
    # Exceptions
    'TabAgentError',
    'AudioProcessingError',
    'TranscriptionError',
    'ModelLoadError',
    'StemSeparationError',
    'TabGenerationError',
    'InvalidAudioError',
    'InvalidTuningError',
    'UnplayableNoteError',
    # Utilities
    'detect_device',
    'validate_audio_path',
    'normalize_audio',
    'midi_to_note_name',
    'note_name_to_midi',
    'format_time',
    'ensure_directory',
    'get_instrument_range',
]
