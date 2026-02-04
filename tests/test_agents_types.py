"""
Tests for agents/types.py - Type Definitions
"""

import pytest
from agents.types import (
    Note, TabNote, AudioAnalysis, Tuning,
    Instrument, Technique, STANDARD_TUNINGS, get_tuning
)


class TestNote:
    """Tests for Note dataclass."""

    @pytest.mark.unit
    def test_note_creation(self):
        """Test basic note creation."""
        note = Note(pitch=60, start_time=0.0, end_time=1.0, velocity=80)
        assert note.pitch == 60
        assert note.start_time == 0.0
        assert note.end_time == 1.0
        assert note.velocity == 80

    @pytest.mark.unit
    def test_note_duration(self):
        """Test note duration property."""
        note = Note(pitch=60, start_time=0.5, end_time=1.5, velocity=80)
        assert note.duration == 1.0

    @pytest.mark.unit
    def test_note_default_velocity(self):
        """Test default velocity."""
        note = Note(pitch=60, start_time=0.0, end_time=1.0)
        assert note.velocity == 80

    @pytest.mark.unit
    def test_note_invalid_pitch_low(self):
        """Test that negative pitch raises ValueError."""
        with pytest.raises(ValueError, match="Pitch must be 0-127"):
            Note(pitch=-1, start_time=0.0, end_time=1.0, velocity=80)

    @pytest.mark.unit
    def test_note_invalid_pitch_high(self):
        """Test that pitch > 127 raises ValueError."""
        with pytest.raises(ValueError, match="Pitch must be 0-127"):
            Note(pitch=128, start_time=0.0, end_time=1.0, velocity=80)

    @pytest.mark.unit
    def test_note_invalid_velocity(self):
        """Test that invalid velocity raises ValueError."""
        with pytest.raises(ValueError, match="Velocity must be 0-127"):
            Note(pitch=60, start_time=0.0, end_time=1.0, velocity=200)

    @pytest.mark.unit
    def test_note_invalid_start_time(self):
        """Test that negative start time raises ValueError."""
        with pytest.raises(ValueError, match="Start time must be non-negative"):
            Note(pitch=60, start_time=-1.0, end_time=1.0, velocity=80)

    @pytest.mark.unit
    def test_note_invalid_end_time(self):
        """Test that end_time < start_time raises ValueError."""
        with pytest.raises(ValueError, match="End time.*must be >= start time"):
            Note(pitch=60, start_time=2.0, end_time=1.0, velocity=80)

    @pytest.mark.unit
    def test_note_zero_duration(self):
        """Test that zero duration note is valid."""
        note = Note(pitch=60, start_time=1.0, end_time=1.0, velocity=80)
        assert note.duration == 0.0


class TestTabNote:
    """Tests for TabNote dataclass."""

    @pytest.mark.unit
    def test_tabnote_creation(self):
        """Test basic TabNote creation."""
        tab = TabNote(string=0, fret=5, start_time=0.0, end_time=0.5,
                      technique="pick", pitch=45)
        assert tab.string == 0
        assert tab.fret == 5
        assert tab.technique == "pick"
        assert tab.pitch == 45

    @pytest.mark.unit
    def test_tabnote_duration(self):
        """Test TabNote duration property."""
        tab = TabNote(string=0, fret=5, start_time=0.5, end_time=1.5)
        assert tab.duration == 1.0

    @pytest.mark.unit
    def test_tabnote_defaults(self):
        """Test TabNote default values."""
        tab = TabNote(string=0, fret=5, start_time=0.0, end_time=0.5)
        assert tab.technique == "pick"
        assert tab.pitch == 0

    @pytest.mark.unit
    def test_tabnote_invalid_string(self):
        """Test that negative string raises ValueError."""
        with pytest.raises(ValueError, match="String index must be non-negative"):
            TabNote(string=-1, fret=5, start_time=0.0, end_time=0.5)

    @pytest.mark.unit
    def test_tabnote_invalid_fret(self):
        """Test that negative fret raises ValueError."""
        with pytest.raises(ValueError, match="Fret number must be non-negative"):
            TabNote(string=0, fret=-1, start_time=0.0, end_time=0.5)

    @pytest.mark.unit
    def test_tabnote_open_string(self):
        """Test open string (fret 0)."""
        tab = TabNote(string=0, fret=0, start_time=0.0, end_time=0.5)
        assert tab.fret == 0


class TestAudioAnalysis:
    """Tests for AudioAnalysis dataclass."""

    @pytest.mark.unit
    def test_audio_analysis_creation(self):
        """Test basic AudioAnalysis creation."""
        analysis = AudioAnalysis(
            is_ai_generated=True,
            confidence=0.85,
            high_freq_ratio=0.2,
            spectral_flatness=0.3,
            temporal_consistency=0.8,
            artifacts_detected=["high_frequency_shimmer"],
            preprocessing_recommended=True
        )
        assert analysis.is_ai_generated is True
        assert analysis.confidence == 0.85
        assert len(analysis.artifacts_detected) == 1

    @pytest.mark.unit
    def test_audio_analysis_defaults(self):
        """Test AudioAnalysis default values."""
        analysis = AudioAnalysis(
            is_ai_generated=False,
            confidence=0.3,
            high_freq_ratio=0.1,
            spectral_flatness=0.5,
            temporal_consistency=0.4
        )
        assert analysis.artifacts_detected == []
        assert analysis.preprocessing_recommended is False

    @pytest.mark.unit
    def test_audio_analysis_invalid_confidence_high(self):
        """Test that confidence > 1 raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be 0-1"):
            AudioAnalysis(
                is_ai_generated=False,
                confidence=1.5,
                high_freq_ratio=0.1,
                spectral_flatness=0.5,
                temporal_consistency=0.4
            )

    @pytest.mark.unit
    def test_audio_analysis_invalid_confidence_low(self):
        """Test that confidence < 0 raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be 0-1"):
            AudioAnalysis(
                is_ai_generated=False,
                confidence=-0.1,
                high_freq_ratio=0.1,
                spectral_flatness=0.5,
                temporal_consistency=0.4
            )


class TestTuning:
    """Tests for Tuning dataclass."""

    @pytest.mark.unit
    def test_tuning_creation(self):
        """Test basic Tuning creation."""
        tuning = Tuning(
            name="Test Tuning",
            pitches=[40, 45, 50, 55, 59, 64],
            instrument=Instrument.GUITAR
        )
        assert tuning.name == "Test Tuning"
        assert tuning.num_strings == 6

    @pytest.mark.unit
    def test_tuning_default_instrument(self):
        """Test default instrument is guitar."""
        tuning = Tuning(name="Test", pitches=[40, 45, 50])
        assert tuning.instrument == Instrument.GUITAR

    @pytest.mark.unit
    def test_tuning_num_strings(self):
        """Test num_strings property."""
        tuning = Tuning(name="4-string", pitches=[28, 33, 38, 43])
        assert tuning.num_strings == 4

    @pytest.mark.unit
    def test_tuning_get_pitch_for_position(self):
        """Test getting pitch for string/fret position."""
        tuning = Tuning(
            name="Standard",
            pitches=[40, 45, 50, 55, 59, 64]
        )
        # Open E string
        assert tuning.get_pitch_for_position(0, 0) == 40
        # E string, 5th fret = A
        assert tuning.get_pitch_for_position(0, 5) == 45
        # High E string open
        assert tuning.get_pitch_for_position(5, 0) == 64

    @pytest.mark.unit
    def test_tuning_invalid_string(self):
        """Test get_pitch_for_position with invalid string."""
        tuning = Tuning(name="Standard", pitches=[40, 45, 50, 55, 59, 64])
        with pytest.raises(ValueError, match="String 6 out of range"):
            tuning.get_pitch_for_position(6, 0)


class TestStandardTunings:
    """Tests for standard tuning definitions."""

    @pytest.mark.unit
    def test_standard_tunings_exist(self):
        """Test that standard tunings are defined."""
        assert "guitar_standard" in STANDARD_TUNINGS
        assert "guitar_drop_d" in STANDARD_TUNINGS
        assert "bass_4_string" in STANDARD_TUNINGS
        assert "bass_5_string" in STANDARD_TUNINGS

    @pytest.mark.unit
    def test_guitar_standard_tuning(self):
        """Test guitar standard tuning values."""
        tuning = STANDARD_TUNINGS["guitar_standard"]
        assert tuning.pitches == [40, 45, 50, 55, 59, 64]
        assert tuning.instrument == Instrument.GUITAR

    @pytest.mark.unit
    def test_bass_tunings(self):
        """Test bass tuning values."""
        bass4 = STANDARD_TUNINGS["bass_4_string"]
        assert bass4.num_strings == 4
        assert bass4.instrument == Instrument.BASS

        bass5 = STANDARD_TUNINGS["bass_5_string"]
        assert bass5.num_strings == 5


class TestGetTuning:
    """Tests for get_tuning function."""

    @pytest.mark.unit
    def test_get_tuning_exact_match(self):
        """Test getting tuning by exact name."""
        tuning = get_tuning("guitar_standard")
        assert tuning is not None
        assert tuning.name == "Guitar (Standard)"

    @pytest.mark.unit
    def test_get_tuning_case_insensitive(self):
        """Test case-insensitive tuning lookup."""
        tuning = get_tuning("GUITAR_STANDARD")
        assert tuning is not None

    @pytest.mark.unit
    def test_get_tuning_not_found(self):
        """Test getting non-existent tuning returns None."""
        tuning = get_tuning("unknown_tuning")
        assert tuning is None


class TestEnums:
    """Tests for enum types."""

    @pytest.mark.unit
    def test_instrument_values(self):
        """Test Instrument enum values."""
        assert Instrument.GUITAR.value == "guitar"
        assert Instrument.BASS.value == "bass"

    @pytest.mark.unit
    def test_technique_values(self):
        """Test Technique enum values."""
        assert Technique.PICK.value == "pick"
        assert Technique.SLIDE.value == "slide"
        assert Technique.HAMMER.value == "hammer"
        assert Technique.PULL.value == "pull"
