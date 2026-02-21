"""
Tab Agent - Utility Functions
Common helper functions used across agents.
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np


def detect_device(preferred: str = "auto") -> str:
    """
    Detect the best available compute device.

    Args:
        preferred: Preferred device ("cpu", "cuda", "mps", or "auto")

    Returns:
        Device string ("cpu", "cuda", or "mps")
    """
    if preferred != "auto":
        return preferred

    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"


def validate_audio_path(audio_path: str) -> Path:
    """
    Validate that an audio file exists and has a supported extension.

    Args:
        audio_path: Path to audio file

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If extension is not supported
    """
    from .exceptions import InvalidAudioError

    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    supported_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'}
    if path.suffix.lower() not in supported_extensions:
        raise InvalidAudioError(
            f"Unsupported audio format: {path.suffix}. "
            f"Supported formats: {', '.join(supported_extensions)}"
        )

    return path


def normalize_audio(audio: np.ndarray, target_peak: float = 0.9) -> np.ndarray:
    """
    Normalize audio to a target peak level.

    Args:
        audio: Audio samples as numpy array
        target_peak: Target peak level (0-1)

    Returns:
        Normalized audio array
    """
    peak = np.max(np.abs(audio))
    if peak > 0:
        return audio * (target_peak / peak)
    return audio


def midi_to_note_name(midi_pitch: int) -> str:
    """
    Convert MIDI pitch number to note name.

    Args:
        midi_pitch: MIDI pitch (0-127)

    Returns:
        Note name (e.g., "C4", "F#3")
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_pitch // 12) - 1
    note = note_names[midi_pitch % 12]
    return f"{note}{octave}"


def note_name_to_midi(note_name: str) -> int:
    """
    Convert note name to MIDI pitch number.

    Args:
        note_name: Note name (e.g., "C4", "F#3")

    Returns:
        MIDI pitch number
    """
    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    # Parse note name
    if len(note_name) >= 2:
        if note_name[1] in ('#', 'b'):
            note = note_name[:2]
            octave = int(note_name[2:])
        else:
            note = note_name[0]
            octave = int(note_name[1:])
    else:
        raise ValueError(f"Invalid note name: {note_name}")

    return note_map[note] + (octave + 1) * 12


def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS.ms format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_instrument_range(instrument: str) -> Tuple[int, int]:
    """
    Get the MIDI pitch range for an instrument.

    Args:
        instrument: "guitar" or "bass"

    Returns:
        Tuple of (min_pitch, max_pitch)
    """
    if instrument.lower() == "bass":
        # 5-string bass: B0 (23) to G4 (67)
        return (23, 67)
    else:
        # 6-string guitar: E2 (40) to E6 (88)
        return (40, 88)


def filter_notes_by_range(
    notes: List,
    min_pitch: int,
    max_pitch: int
) -> List:
    """
    Filter notes to only include those within a pitch range.

    Args:
        notes: List of Note objects
        min_pitch: Minimum MIDI pitch
        max_pitch: Maximum MIDI pitch

    Returns:
        Filtered list of notes
    """
    return [n for n in notes if min_pitch <= n.pitch <= max_pitch]


def calculate_tempo_from_notes(notes: List, default_bpm: float = 120.0) -> float:
    """
    Estimate tempo from note timing.

    Args:
        notes: List of Note objects
        default_bpm: Default BPM if estimation fails

    Returns:
        Estimated BPM
    """
    if len(notes) < 2:
        return default_bpm

    # Calculate inter-onset intervals
    onsets = sorted([n.start_time for n in notes])
    intervals = np.diff(onsets)

    if len(intervals) == 0:
        return default_bpm

    # Filter out very short or very long intervals
    valid_intervals = intervals[(intervals > 0.1) & (intervals < 2.0)]

    if len(valid_intervals) == 0:
        return default_bpm

    # Estimate BPM from median interval
    median_interval = np.median(valid_intervals)
    estimated_bpm = 60.0 / median_interval

    # Clamp to reasonable range
    return max(40.0, min(200.0, estimated_bpm))
