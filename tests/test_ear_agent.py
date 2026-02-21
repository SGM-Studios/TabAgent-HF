"""
Tests for agents/ear.py - EarAgent (Audio to MIDI Transcription)
"""

import pytest
from pathlib import Path
from agents import EarAgent
from agents.types import Note


class TestEarAgentInit:
    """Tests for EarAgent initialization."""

    @pytest.mark.unit
    def test_init_default(self):
        """Test default initialization."""
        agent = EarAgent()
        assert agent.model_name == "basic_pitch"
        assert agent._model_loaded is False

    @pytest.mark.unit
    def test_init_with_model(self):
        """Test initialization with specific model."""
        agent = EarAgent(model="yourmt3")
        assert agent.model_name == "yourmt3"

    @pytest.mark.unit
    def test_init_with_device(self):
        """Test initialization with specific device."""
        agent = EarAgent(device="cpu")
        assert agent.device == "cpu"

    @pytest.mark.unit
    def test_init_auto_device(self):
        """Test auto device detection."""
        agent = EarAgent(device="auto")
        assert agent.device in ["cpu", "cuda", "mps"]


class TestDeviceDetection:
    """Tests for device detection."""

    @pytest.mark.unit
    def test_detect_device_explicit(self):
        """Test explicit device selection."""
        agent = EarAgent(device="cpu")
        assert agent._detect_device("cpu") == "cpu"

    @pytest.mark.unit
    def test_detect_device_auto(self):
        """Test auto device detection."""
        agent = EarAgent()
        device = agent._detect_device("auto")
        assert device in ["cpu", "cuda", "mps"]


class TestFilterByRange:
    """Tests for _filter_by_range method."""

    @pytest.mark.unit
    def test_filter_guitar_range(self, ear_agent, sample_notes):
        """Test filtering notes to guitar range."""
        # Add some out-of-range notes
        notes = sample_notes + [
            Note(pitch=20, start_time=3.0, end_time=3.5, velocity=80),  # Too low
            Note(pitch=100, start_time=3.5, end_time=4.0, velocity=80),  # Too high
        ]

        filtered = ear_agent._filter_by_range(notes, "guitar")

        # Original notes should all be in range
        assert len(filtered) <= len(notes)
        for note in filtered:
            assert 40 <= note.pitch <= 88

    @pytest.mark.unit
    def test_filter_bass_range(self, ear_agent, sample_notes_bass):
        """Test filtering notes to bass range."""
        # Add some out-of-range notes
        notes = sample_notes_bass + [
            Note(pitch=10, start_time=2.0, end_time=2.5, velocity=80),  # Too low
            Note(pitch=80, start_time=2.5, end_time=3.0, velocity=80),  # Too high for bass
        ]

        filtered = ear_agent._filter_by_range(notes, "bass")

        for note in filtered:
            assert 23 <= note.pitch <= 67


class TestHumanizeAndClean:
    """Tests for _humanize_and_clean method."""

    @pytest.mark.unit
    def test_removes_very_short_notes(self, ear_agent):
        """Test that very short notes are removed."""
        notes = [
            Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80),  # Normal
            Note(pitch=62, start_time=0.5, end_time=0.51, velocity=80),  # Too short
            Note(pitch=64, start_time=0.6, end_time=1.0, velocity=80),  # Normal
        ]

        cleaned = ear_agent._humanize_and_clean(notes, "guitar")

        assert len(cleaned) == 2
        assert cleaned[0].pitch == 60
        assert cleaned[1].pitch == 64

    @pytest.mark.unit
    def test_removes_octave_doubling(self, ear_agent):
        """Test that octave doubling is detected and removed."""
        notes = [
            Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80),  # C4
            Note(pitch=72, start_time=0.0, end_time=0.5, velocity=80),  # C5 (octave)
        ]

        cleaned = ear_agent._humanize_and_clean(notes, "guitar")

        # Should keep only one
        assert len(cleaned) == 1

    @pytest.mark.unit
    def test_keeps_non_octave_simultaneous(self, ear_agent):
        """Test that non-octave simultaneous notes are kept."""
        notes = [
            Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80),  # C4
            Note(pitch=64, start_time=0.0, end_time=0.5, velocity=80),  # E4
        ]

        cleaned = ear_agent._humanize_and_clean(notes, "guitar")

        assert len(cleaned) == 2

    @pytest.mark.unit
    def test_empty_notes(self, ear_agent):
        """Test cleaning empty notes list."""
        cleaned = ear_agent._humanize_and_clean([], "guitar")
        assert len(cleaned) == 0


class TestGenerateMockNotes:
    """Tests for mock note generation."""

    @pytest.mark.unit
    def test_mock_guitar_notes(self, ear_agent):
        """Test mock guitar note generation."""
        notes = ear_agent._generate_mock_notes("guitar")

        assert len(notes) == 8
        for note in notes:
            assert note.pitch >= 40  # Guitar range

    @pytest.mark.unit
    def test_mock_bass_notes(self, ear_agent):
        """Test mock bass note generation."""
        notes = ear_agent._generate_mock_notes("bass")

        assert len(notes) == 8
        for note in notes:
            assert note.pitch >= 28  # Bass range

    @pytest.mark.unit
    def test_mock_notes_have_timing(self, ear_agent):
        """Test that mock notes have proper timing."""
        notes = ear_agent._generate_mock_notes("guitar")

        for i, note in enumerate(notes):
            assert note.start_time == pytest.approx(i * 0.5)
            assert note.end_time == pytest.approx(i * 0.5 + 0.4)


class TestTranscribeStem:
    """Tests for transcribe_stem method (with mocking)."""

    @pytest.mark.unit
    def test_transcribe_uses_mock_when_no_model(self, ear_agent, sample_audio_mono):
        """Test that transcription falls back to mock mode."""
        # Force mock mode by not loading model
        ear_agent.predict_fn = None
        ear_agent._model_loaded = True

        notes = ear_agent.transcribe_stem(sample_audio_mono, target="guitar")

        assert len(notes) > 0
        assert all(isinstance(n, Note) for n in notes)

    @pytest.mark.unit
    def test_transcribe_returns_notes(self, ear_agent, sample_audio_mono):
        """Test that transcribe returns Note objects."""
        # This will use mock mode in testing
        notes = ear_agent.transcribe_stem(sample_audio_mono, target="guitar")

        assert isinstance(notes, list)
        for note in notes:
            assert isinstance(note, Note)


class TestExportMidi:
    """Tests for MIDI export."""

    @pytest.mark.unit
    def test_export_midi_creates_file(self, ear_agent, sample_notes, temp_dir):
        """Test that MIDI export creates a file."""
        output_path = str(temp_dir / "test_output.mid")

        ear_agent.export_midi(sample_notes, output_path)

        assert Path(output_path).exists()

    @pytest.mark.unit
    def test_export_midi_empty_notes(self, ear_agent, temp_dir):
        """Test MIDI export with empty notes."""
        output_path = str(temp_dir / "empty.mid")

        ear_agent.export_midi([], output_path)

        # Should still create file
        assert Path(output_path).exists()

    @pytest.mark.integration
    def test_export_midi_with_tempo(self, ear_agent, sample_notes, temp_dir):
        """Test MIDI export with custom tempo."""
        output_path = str(temp_dir / "tempo_test.mid")

        ear_agent.export_midi(sample_notes, output_path, tempo=100)

        assert Path(output_path).exists()
