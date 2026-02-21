"""
Tab Agent - Shared Type Definitions
Centralized dataclasses and type definitions for the agents module.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Instrument(Enum):
    """Supported instrument types."""
    GUITAR = "guitar"
    BASS = "bass"


class Technique(Enum):
    """Guitar/bass playing techniques."""
    PICK = "pick"
    SLIDE = "slide"
    HAMMER = "hammer"
    PULL = "pull"
    BEND = "bend"
    VIBRATO = "vibrato"
    TAP = "tap"
    MUTE = "mute"


@dataclass
class Note:
    """
    Simplified note representation from audio transcription.

    Attributes:
        pitch: MIDI pitch number (0-127)
        start_time: Start time in seconds
        end_time: End time in seconds
        velocity: MIDI velocity (0-127)
    """
    pitch: int
    start_time: float
    end_time: float
    velocity: int = 80

    @property
    def duration(self) -> float:
        """Calculate note duration in seconds."""
        return self.end_time - self.start_time

    def __post_init__(self):
        """Validate note parameters."""
        if not 0 <= self.pitch <= 127:
            raise ValueError(f"Pitch must be 0-127, got {self.pitch}")
        if not 0 <= self.velocity <= 127:
            raise ValueError(f"Velocity must be 0-127, got {self.velocity}")
        if self.start_time < 0:
            raise ValueError(f"Start time must be non-negative, got {self.start_time}")
        if self.end_time < self.start_time:
            raise ValueError(f"End time ({self.end_time}) must be >= start time ({self.start_time})")


@dataclass
class TabNote:
    """
    A note positioned on the fretboard.

    Attributes:
        string: String index (0 = lowest pitched string)
        fret: Fret number (0 = open string)
        start_time: Start time in seconds
        end_time: End time in seconds
        technique: Playing technique
        pitch: Original MIDI pitch
    """
    string: int
    fret: int
    start_time: float
    end_time: float
    technique: str = "pick"
    pitch: int = 0

    @property
    def duration(self) -> float:
        """Calculate note duration in seconds."""
        return self.end_time - self.start_time

    def __post_init__(self):
        """Validate tab note parameters."""
        if self.string < 0:
            raise ValueError(f"String index must be non-negative, got {self.string}")
        if self.fret < 0:
            raise ValueError(f"Fret number must be non-negative, got {self.fret}")


@dataclass
class AudioAnalysis:
    """
    Results from AI-generated audio detection.

    Attributes:
        is_ai_generated: Whether the audio appears to be AI-generated
        confidence: Confidence score (0-1)
        high_freq_ratio: Ratio of high frequency energy
        spectral_flatness: Spectral flatness measure
        temporal_consistency: Temporal consistency measure
        artifacts_detected: List of detected artifact types
        preprocessing_recommended: Whether preprocessing is recommended
    """
    is_ai_generated: bool
    confidence: float
    high_freq_ratio: float
    spectral_flatness: float
    temporal_consistency: float
    artifacts_detected: List[str] = field(default_factory=list)
    preprocessing_recommended: bool = False

    def __post_init__(self):
        """Validate analysis parameters."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")


@dataclass
class Tuning:
    """
    Instrument tuning definition.

    Attributes:
        name: Human-readable tuning name
        pitches: List of MIDI pitch numbers for open strings (low to high)
        instrument: Instrument type
    """
    name: str
    pitches: List[int]
    instrument: Instrument = Instrument.GUITAR

    @property
    def num_strings(self) -> int:
        """Return the number of strings."""
        return len(self.pitches)

    def get_pitch_for_position(self, string: int, fret: int) -> int:
        """Calculate the MIDI pitch for a string/fret position."""
        if not 0 <= string < len(self.pitches):
            raise ValueError(f"String {string} out of range (0-{len(self.pitches)-1})")
        return self.pitches[string] + fret


# Standard tuning definitions
STANDARD_TUNINGS = {
    "guitar_standard": Tuning(
        name="Guitar (Standard)",
        pitches=[40, 45, 50, 55, 59, 64],  # E2-A2-D3-G3-B3-E4
        instrument=Instrument.GUITAR
    ),
    "guitar_drop_d": Tuning(
        name="Guitar (Drop D)",
        pitches=[38, 45, 50, 55, 59, 64],  # D2-A2-D3-G3-B3-E4
        instrument=Instrument.GUITAR
    ),
    "guitar_half_step_down": Tuning(
        name="Guitar (Half Step Down)",
        pitches=[39, 44, 49, 54, 58, 63],  # Eb2-Ab2-Db3-Gb3-Bb3-Eb4
        instrument=Instrument.GUITAR
    ),
    "bass_4_string": Tuning(
        name="Bass (4-String)",
        pitches=[28, 33, 38, 43],  # E1-A1-D2-G2
        instrument=Instrument.BASS
    ),
    "bass_5_string": Tuning(
        name="Bass (5-String)",
        pitches=[23, 28, 33, 38, 43],  # B0-E1-A1-D2-G2
        instrument=Instrument.BASS
    ),
}


def get_tuning(name: str) -> Optional[Tuning]:
    """
    Get a standard tuning by name.

    Args:
        name: Tuning name (case-insensitive, underscores optional)

    Returns:
        Tuning object or None if not found
    """
    key = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    return STANDARD_TUNINGS.get(key)
