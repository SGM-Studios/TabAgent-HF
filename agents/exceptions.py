"""
Tab Agent - Custom Exceptions
Centralized exception definitions for better error handling.
"""


class TabAgentError(Exception):
    """Base exception for Tab Agent errors."""
    pass


class AudioProcessingError(TabAgentError):
    """Error during audio processing."""
    pass


class TranscriptionError(TabAgentError):
    """Error during audio transcription."""
    pass


class ModelLoadError(TabAgentError):
    """Error loading ML model."""
    pass


class StemSeparationError(TabAgentError):
    """Error during stem separation."""
    pass


class TabGenerationError(TabAgentError):
    """Error during tablature generation."""
    pass


class InvalidAudioError(TabAgentError):
    """Invalid or unsupported audio file."""
    pass


class InvalidTuningError(TabAgentError):
    """Invalid tuning configuration."""
    pass


class UnplayableNoteError(TabAgentError):
    """Note cannot be played on the instrument."""
    pass
