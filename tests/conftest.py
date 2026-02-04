"""
Tab Agent Pro - Test Configuration and Fixtures
Shared fixtures for all test modules.
"""

import os
import tempfile
from pathlib import Path
from typing import List
import pytest
import numpy as np


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_data_dir():
    """Return the path to test data directory."""
    return Path(__file__).parent / "test_data"


# ============================================================================
# Audio Fixtures
# ============================================================================

@pytest.fixture
def sample_audio_mono(temp_dir):
    """Create a sample mono audio file (sine wave)."""
    import soundfile as sf

    sr = 22050
    duration = 2.0  # seconds
    freq = 440.0  # A4

    t = np.linspace(0, duration, int(sr * duration), False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)

    path = temp_dir / "test_mono.wav"
    sf.write(str(path), audio, sr)

    return str(path)


@pytest.fixture
def sample_audio_stereo(temp_dir):
    """Create a sample stereo audio file."""
    import soundfile as sf

    sr = 22050
    duration = 2.0
    freq_l = 440.0
    freq_r = 554.37  # C#5

    t = np.linspace(0, duration, int(sr * duration), False)
    left = 0.5 * np.sin(2 * np.pi * freq_l * t)
    right = 0.5 * np.sin(2 * np.pi * freq_r * t)
    audio = np.vstack([left, right]).T

    path = temp_dir / "test_stereo.wav"
    sf.write(str(path), audio, sr)

    return str(path)


@pytest.fixture
def sample_audio_with_beats(temp_dir):
    """Create an audio file with clear beat patterns."""
    import soundfile as sf

    sr = 22050
    duration = 4.0
    bpm = 120
    beat_interval = 60.0 / bpm

    t = np.linspace(0, duration, int(sr * duration), False)
    audio = np.zeros_like(t)

    # Add click sounds at beat positions
    for beat_time in np.arange(0, duration, beat_interval):
        beat_idx = int(beat_time * sr)
        click_len = int(0.01 * sr)  # 10ms click
        if beat_idx + click_len < len(audio):
            # Create a click (short burst)
            click = np.exp(-np.linspace(0, 10, click_len)) * np.sin(
                2 * np.pi * 1000 * np.linspace(0, 0.01, click_len)
            )
            audio[beat_idx:beat_idx + click_len] += click

    # Normalize
    audio = audio / (np.max(np.abs(audio)) + 1e-8) * 0.8

    path = temp_dir / "test_beats.wav"
    sf.write(str(path), audio, sr)

    return str(path)


@pytest.fixture
def sample_audio_complex(temp_dir):
    """Create a more complex audio file with multiple frequencies."""
    import soundfile as sf

    sr = 22050
    duration = 3.0

    t = np.linspace(0, duration, int(sr * duration), False)

    # Multiple harmonics
    audio = np.zeros_like(t)
    for i, freq in enumerate([82.41, 110.0, 146.83, 196.0, 246.94]):  # E2-B3 (guitar notes)
        amplitude = 1.0 / (i + 1)
        audio += amplitude * np.sin(2 * np.pi * freq * t)

    # Add some noise
    audio += 0.01 * np.random.randn(len(audio))

    # Normalize
    audio = audio / (np.max(np.abs(audio)) + 1e-8) * 0.7

    path = temp_dir / "test_complex.wav"
    sf.write(str(path), audio, sr)

    return str(path)


# ============================================================================
# Note Fixtures
# ============================================================================

@pytest.fixture
def sample_notes():
    """Create sample Note objects for testing."""
    from agents.types import Note

    return [
        Note(pitch=40, start_time=0.0, end_time=0.5, velocity=80),
        Note(pitch=45, start_time=0.5, end_time=1.0, velocity=85),
        Note(pitch=50, start_time=1.0, end_time=1.5, velocity=90),
        Note(pitch=55, start_time=1.5, end_time=2.0, velocity=85),
        Note(pitch=59, start_time=2.0, end_time=2.5, velocity=80),
        Note(pitch=64, start_time=2.5, end_time=3.0, velocity=75),
    ]


@pytest.fixture
def sample_notes_guitar():
    """Create sample guitar notes (E2 to E6 range)."""
    from agents.types import Note

    return [
        Note(pitch=40, start_time=0.0, end_time=0.3, velocity=80),  # E2
        Note(pitch=52, start_time=0.3, end_time=0.6, velocity=85),  # E3
        Note(pitch=55, start_time=0.6, end_time=0.9, velocity=90),  # G3
        Note(pitch=60, start_time=0.9, end_time=1.2, velocity=85),  # C4
        Note(pitch=64, start_time=1.2, end_time=1.5, velocity=80),  # E4
    ]


@pytest.fixture
def sample_notes_bass():
    """Create sample bass notes (B0 to G4 range)."""
    from agents.types import Note

    return [
        Note(pitch=28, start_time=0.0, end_time=0.5, velocity=90),  # E1
        Note(pitch=33, start_time=0.5, end_time=1.0, velocity=85),  # A1
        Note(pitch=38, start_time=1.0, end_time=1.5, velocity=80),  # D2
        Note(pitch=43, start_time=1.5, end_time=2.0, velocity=85),  # G2
    ]


@pytest.fixture
def sample_notes_chord():
    """Create notes that form a chord (simultaneous notes)."""
    from agents.types import Note

    # E major chord
    return [
        Note(pitch=40, start_time=0.0, end_time=1.0, velocity=80),  # E2
        Note(pitch=47, start_time=0.0, end_time=1.0, velocity=75),  # B2
        Note(pitch=52, start_time=0.0, end_time=1.0, velocity=70),  # E3
        Note(pitch=56, start_time=0.0, end_time=1.0, velocity=75),  # G#3
        Note(pitch=59, start_time=0.0, end_time=1.0, velocity=70),  # B3
        Note(pitch=64, start_time=0.0, end_time=1.0, velocity=75),  # E4
    ]


# ============================================================================
# Tuning Fixtures
# ============================================================================

@pytest.fixture
def guitar_standard_tuning():
    """Standard guitar tuning (MIDI pitches)."""
    return [40, 45, 50, 55, 59, 64]


@pytest.fixture
def guitar_drop_d_tuning():
    """Drop D guitar tuning."""
    return [38, 45, 50, 55, 59, 64]


@pytest.fixture
def bass_4_string_tuning():
    """4-string bass tuning."""
    return [28, 33, 38, 43]


@pytest.fixture
def bass_5_string_tuning():
    """5-string bass tuning."""
    return [23, 28, 33, 38, 43]


# ============================================================================
# Agent Fixtures
# ============================================================================

@pytest.fixture
def ear_agent():
    """Create an EarAgent instance (mock mode)."""
    from agents import EarAgent
    return EarAgent(model="basic_pitch", device="cpu")


@pytest.fixture
def tab_agent(guitar_standard_tuning):
    """Create a TabAgent instance."""
    from agents import TabAgent
    return TabAgent(tuning=guitar_standard_tuning, num_frets=24, instrument="guitar")


@pytest.fixture
def tab_agent_bass(bass_4_string_tuning):
    """Create a TabAgent instance for bass."""
    from agents import TabAgent
    return TabAgent(tuning=bass_4_string_tuning, num_frets=24, instrument="bass")


@pytest.fixture
def splitter_agent(temp_dir):
    """Create a SplitterAgent instance."""
    from agents import SplitterAgent
    return SplitterAgent(output_dir=str(temp_dir / "stems"))


@pytest.fixture
def suno_detector():
    """Create a SunoDetector instance."""
    from agents import SunoDetector
    return SunoDetector()


# ============================================================================
# Deforum Fixtures
# ============================================================================

@pytest.fixture
def audio_sync_engine():
    """Create an AudioSyncEngine instance."""
    from deforum import AudioSyncEngine
    return AudioSyncEngine(fps=15)


@pytest.fixture
def deforum_generator():
    """Create a DeforumGenerator instance."""
    from deforum import DeforumGenerator
    return DeforumGenerator(device="cpu", fps=15)


@pytest.fixture
def sample_audio_features():
    """Create sample AudioFeatures for testing."""
    from deforum.types import AudioFeatures

    return AudioFeatures(
        duration=5.0,
        bpm=120.0,
        beat_times=np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]),
        onset_times=np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]),
        onset_strengths=np.array([1.0, 0.5, 0.8, 0.4, 0.9, 0.6, 0.7, 0.5, 0.8]),
        rms_curve=np.linspace(0.3, 0.8, 100),
        spectral_curve=np.random.rand(100),
        sample_rate=22050
    )


@pytest.fixture
def sample_keyframes():
    """Create sample AnimationKeyframes for testing."""
    from deforum.types import AnimationKeyframe

    return [
        AnimationKeyframe(frame=i, time=i / 15.0, zoom=1.0 + i * 0.01, angle=i * 0.5)
        for i in range(30)
    ]


# ============================================================================
# Skip Markers
# ============================================================================

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "gpu: GPU-required tests")


# ============================================================================
# Helper Functions
# ============================================================================

def assert_audio_valid(audio: np.ndarray, sr: int):
    """Assert that audio data is valid."""
    assert audio is not None
    assert len(audio) > 0
    assert sr > 0
    assert not np.isnan(audio).any()
    assert not np.isinf(audio).any()


def assert_notes_valid(notes: List):
    """Assert that note list is valid."""
    assert notes is not None
    for note in notes:
        assert note.pitch >= 0
        assert note.start_time >= 0
        assert note.end_time >= note.start_time
        assert 0 <= note.velocity <= 127
