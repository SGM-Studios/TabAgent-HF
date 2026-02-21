"""
Tests for agents/utils.py - Utility Functions
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from agents.utils import (
    detect_device,
    validate_audio_path,
    normalize_audio,
    midi_to_note_name,
    note_name_to_midi,
    format_time,
    ensure_directory,
    get_instrument_range,
    filter_notes_by_range,
    calculate_tempo_from_notes,
)
from agents.exceptions import InvalidAudioError


class TestDetectDevice:
    """Tests for detect_device function."""

    @pytest.mark.unit
    def test_detect_device_explicit_cpu(self):
        """Test explicit CPU selection."""
        assert detect_device("cpu") == "cpu"

    @pytest.mark.unit
    def test_detect_device_explicit_cuda(self):
        """Test explicit CUDA selection."""
        assert detect_device("cuda") == "cuda"

    @pytest.mark.unit
    def test_detect_device_auto(self):
        """Test auto detection returns valid device."""
        device = detect_device("auto")
        assert device in ["cpu", "cuda", "mps"]


class TestValidateAudioPath:
    """Tests for validate_audio_path function."""

    @pytest.mark.unit
    def test_validate_existing_wav(self, sample_audio_mono):
        """Test validating existing WAV file."""
        path = validate_audio_path(sample_audio_mono)
        assert path.exists()
        assert path.suffix == ".wav"

    @pytest.mark.unit
    def test_validate_nonexistent_file(self):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_audio_path("/nonexistent/path/audio.wav")

    @pytest.mark.unit
    def test_validate_unsupported_format(self, temp_dir):
        """Test that unsupported format raises InvalidAudioError."""
        bad_file = temp_dir / "test.txt"
        bad_file.write_text("not audio")

        with pytest.raises(InvalidAudioError, match="Unsupported audio format"):
            validate_audio_path(str(bad_file))


class TestNormalizeAudio:
    """Tests for normalize_audio function."""

    @pytest.mark.unit
    def test_normalize_basic(self):
        """Test basic normalization."""
        audio = np.array([0.5, -0.5, 0.25, -0.25])
        normalized = normalize_audio(audio, target_peak=0.9)

        assert np.max(np.abs(normalized)) == pytest.approx(0.9)

    @pytest.mark.unit
    def test_normalize_already_loud(self):
        """Test normalizing already loud audio."""
        audio = np.array([1.0, -1.0, 0.5, -0.5])
        normalized = normalize_audio(audio, target_peak=0.5)

        assert np.max(np.abs(normalized)) == pytest.approx(0.5)

    @pytest.mark.unit
    def test_normalize_silence(self):
        """Test normalizing silence (all zeros)."""
        audio = np.zeros(100)
        normalized = normalize_audio(audio, target_peak=0.9)

        assert np.all(normalized == 0)

    @pytest.mark.unit
    def test_normalize_preserves_shape(self):
        """Test that normalization preserves array shape."""
        audio = np.random.randn(1000) * 0.3
        normalized = normalize_audio(audio)

        assert normalized.shape == audio.shape


class TestMidiToNoteName:
    """Tests for midi_to_note_name function."""

    @pytest.mark.unit
    def test_middle_c(self):
        """Test middle C (MIDI 60)."""
        assert midi_to_note_name(60) == "C4"

    @pytest.mark.unit
    def test_a440(self):
        """Test A440 (MIDI 69)."""
        assert midi_to_note_name(69) == "A4"

    @pytest.mark.unit
    def test_low_e_guitar(self):
        """Test low E on guitar (MIDI 40)."""
        assert midi_to_note_name(40) == "E2"

    @pytest.mark.unit
    def test_sharps(self):
        """Test sharp notes."""
        assert midi_to_note_name(61) == "C#4"
        assert midi_to_note_name(66) == "F#4"

    @pytest.mark.unit
    def test_low_notes(self):
        """Test low notes."""
        assert midi_to_note_name(21) == "A0"  # Lowest piano key
        assert midi_to_note_name(23) == "B0"  # Low B on 5-string bass


class TestNoteNameToMidi:
    """Tests for note_name_to_midi function."""

    @pytest.mark.unit
    def test_middle_c(self):
        """Test middle C."""
        assert note_name_to_midi("C4") == 60

    @pytest.mark.unit
    def test_a440(self):
        """Test A440."""
        assert note_name_to_midi("A4") == 69

    @pytest.mark.unit
    def test_sharp_note(self):
        """Test sharp notes."""
        assert note_name_to_midi("C#4") == 61
        assert note_name_to_midi("F#4") == 66

    @pytest.mark.unit
    def test_flat_note(self):
        """Test flat notes."""
        assert note_name_to_midi("Db4") == 61
        assert note_name_to_midi("Bb3") == 58

    @pytest.mark.unit
    def test_roundtrip(self):
        """Test that midi_to_note_name and note_name_to_midi are consistent."""
        for midi in range(21, 108):  # Piano range
            name = midi_to_note_name(midi)
            back = note_name_to_midi(name)
            assert back == midi

    @pytest.mark.unit
    def test_invalid_note_name(self):
        """Test invalid note name raises ValueError."""
        with pytest.raises((ValueError, KeyError)):
            note_name_to_midi("X4")


class TestFormatTime:
    """Tests for format_time function."""

    @pytest.mark.unit
    def test_zero(self):
        """Test formatting zero seconds."""
        assert format_time(0.0) == "00:00.00"

    @pytest.mark.unit
    def test_seconds_only(self):
        """Test formatting seconds only."""
        assert format_time(5.25) == "00:05.25"

    @pytest.mark.unit
    def test_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        assert format_time(65.5) == "01:05.50"

    @pytest.mark.unit
    def test_large_time(self):
        """Test formatting larger times."""
        assert format_time(3661.0) == "61:01.00"


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    @pytest.mark.unit
    def test_create_new_directory(self, temp_dir):
        """Test creating a new directory."""
        new_dir = temp_dir / "new_subdir"
        assert not new_dir.exists()

        result = ensure_directory(str(new_dir))

        assert result.exists()
        assert result.is_dir()

    @pytest.mark.unit
    def test_existing_directory(self, temp_dir):
        """Test with existing directory."""
        result = ensure_directory(str(temp_dir))
        assert result.exists()

    @pytest.mark.unit
    def test_nested_directories(self, temp_dir):
        """Test creating nested directories."""
        nested = temp_dir / "a" / "b" / "c"
        result = ensure_directory(str(nested))

        assert result.exists()
        assert result.is_dir()


class TestGetInstrumentRange:
    """Tests for get_instrument_range function."""

    @pytest.mark.unit
    def test_guitar_range(self):
        """Test guitar pitch range."""
        min_pitch, max_pitch = get_instrument_range("guitar")
        assert min_pitch == 40  # E2
        assert max_pitch == 88  # E6

    @pytest.mark.unit
    def test_bass_range(self):
        """Test bass pitch range."""
        min_pitch, max_pitch = get_instrument_range("bass")
        assert min_pitch == 23  # B0
        assert max_pitch == 67  # G4

    @pytest.mark.unit
    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert get_instrument_range("GUITAR") == get_instrument_range("guitar")
        assert get_instrument_range("Bass") == get_instrument_range("bass")


class TestFilterNotesByRange:
    """Tests for filter_notes_by_range function."""

    @pytest.mark.unit
    def test_filter_basic(self, sample_notes):
        """Test basic filtering."""
        # Filter to narrow range
        filtered = filter_notes_by_range(sample_notes, 45, 60)

        for note in filtered:
            assert 45 <= note.pitch <= 60

    @pytest.mark.unit
    def test_filter_empty_result(self, sample_notes):
        """Test filtering that results in empty list."""
        filtered = filter_notes_by_range(sample_notes, 100, 127)
        assert len(filtered) == 0

    @pytest.mark.unit
    def test_filter_all_pass(self, sample_notes):
        """Test filtering where all notes pass."""
        filtered = filter_notes_by_range(sample_notes, 0, 127)
        assert len(filtered) == len(sample_notes)

    @pytest.mark.unit
    def test_filter_empty_input(self):
        """Test filtering empty list."""
        filtered = filter_notes_by_range([], 40, 80)
        assert len(filtered) == 0


class TestCalculateTempoFromNotes:
    """Tests for calculate_tempo_from_notes function."""

    @pytest.mark.unit
    def test_tempo_estimation(self):
        """Test basic tempo estimation."""
        from agents.types import Note

        # Create notes at 120 BPM (0.5s intervals)
        notes = [
            Note(pitch=60, start_time=i * 0.5, end_time=i * 0.5 + 0.4, velocity=80)
            for i in range(8)
        ]

        tempo = calculate_tempo_from_notes(notes)
        assert 100 <= tempo <= 140  # Should be around 120

    @pytest.mark.unit
    def test_tempo_empty_notes(self):
        """Test tempo calculation with empty notes."""
        tempo = calculate_tempo_from_notes([], default_bpm=100.0)
        assert tempo == 100.0

    @pytest.mark.unit
    def test_tempo_single_note(self):
        """Test tempo calculation with single note."""
        from agents.types import Note

        notes = [Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80)]
        tempo = calculate_tempo_from_notes(notes, default_bpm=120.0)
        assert tempo == 120.0  # Should return default

    @pytest.mark.unit
    def test_tempo_clamped_to_range(self):
        """Test that tempo is clamped to reasonable range."""
        from agents.types import Note

        # Very fast notes
        notes = [
            Note(pitch=60, start_time=i * 0.05, end_time=i * 0.05 + 0.03, velocity=80)
            for i in range(10)
        ]

        tempo = calculate_tempo_from_notes(notes)
        assert tempo <= 200.0  # Should be clamped
