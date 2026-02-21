"""
Tests for deforum/audio_sync.py - AudioSyncEngine
"""

import pytest
import numpy as np
from deforum import AudioSyncEngine
from deforum.types import AudioFeatures, AnimationKeyframe


class TestAudioSyncEngineInit:
    """Tests for AudioSyncEngine initialization."""

    @pytest.mark.unit
    def test_init_default(self):
        """Test default initialization."""
        engine = AudioSyncEngine()
        assert engine.fps == 15
        assert engine.onset_sensitivity == 0.5
        assert engine.beat_strength_scale == 2.0

    @pytest.mark.unit
    def test_init_custom(self):
        """Test initialization with custom parameters."""
        engine = AudioSyncEngine(
            fps=30,
            onset_sensitivity=0.7,
            beat_strength_scale=1.5
        )
        assert engine.fps == 30
        assert engine.onset_sensitivity == 0.7
        assert engine.beat_strength_scale == 1.5


class TestAnalyzeAudio:
    """Tests for analyze_audio method."""

    @pytest.mark.unit
    def test_analyze_returns_features(self, audio_sync_engine, sample_audio_mono):
        """Test that analyze returns AudioFeatures."""
        features = audio_sync_engine.analyze_audio(sample_audio_mono)

        assert isinstance(features, AudioFeatures)
        assert features.duration > 0
        assert features.bpm > 0
        assert features.sample_rate > 0

    @pytest.mark.unit
    def test_analyze_beat_times(self, audio_sync_engine, sample_audio_with_beats):
        """Test beat detection on audio with beats."""
        features = audio_sync_engine.analyze_audio(sample_audio_with_beats)

        assert len(features.beat_times) > 0
        # Beat times should be sorted
        assert np.all(np.diff(features.beat_times) >= 0)

    @pytest.mark.unit
    def test_analyze_onset_times(self, audio_sync_engine, sample_audio_mono):
        """Test onset detection."""
        features = audio_sync_engine.analyze_audio(sample_audio_mono)

        assert isinstance(features.onset_times, np.ndarray)
        assert isinstance(features.onset_strengths, np.ndarray)

    @pytest.mark.unit
    def test_analyze_normalized_curves(self, audio_sync_engine, sample_audio_mono):
        """Test that curves are normalized."""
        features = audio_sync_engine.analyze_audio(sample_audio_mono)

        # RMS curve should be normalized 0-1
        if len(features.rms_curve) > 0:
            assert np.max(features.rms_curve) <= 1.0
            assert np.min(features.rms_curve) >= 0.0

        # Spectral curve should be normalized 0-1
        if len(features.spectral_curve) > 0:
            assert np.max(features.spectral_curve) <= 1.0
            assert np.min(features.spectral_curve) >= 0.0


class TestGenerateKeyframes:
    """Tests for generate_keyframes method."""

    @pytest.mark.unit
    def test_generate_keyframes_basic(self, audio_sync_engine, sample_audio_features):
        """Test basic keyframe generation."""
        keyframes = audio_sync_engine.generate_keyframes(sample_audio_features)

        assert len(keyframes) > 0
        assert all(isinstance(kf, AnimationKeyframe) for kf in keyframes)

    @pytest.mark.unit
    def test_generate_keyframes_count(self, audio_sync_engine, sample_audio_features):
        """Test keyframe count respects max_frames."""
        max_frames = 30
        keyframes = audio_sync_engine.generate_keyframes(
            sample_audio_features, max_frames=max_frames
        )

        assert len(keyframes) <= max_frames

    @pytest.mark.unit
    def test_generate_keyframes_frame_numbers(self, audio_sync_engine, sample_audio_features):
        """Test that frame numbers are sequential."""
        keyframes = audio_sync_engine.generate_keyframes(sample_audio_features)

        for i, kf in enumerate(keyframes):
            assert kf.frame == i

    @pytest.mark.unit
    def test_generate_keyframes_timing(self, audio_sync_engine, sample_audio_features):
        """Test that keyframe timing matches FPS."""
        keyframes = audio_sync_engine.generate_keyframes(sample_audio_features)

        for kf in keyframes:
            expected_time = kf.frame / audio_sync_engine.fps
            assert kf.time == pytest.approx(expected_time, abs=0.001)

    @pytest.mark.unit
    def test_generate_keyframes_styles(self, audio_sync_engine, sample_audio_features):
        """Test keyframe generation with different styles."""
        styles = ["guitar_hero", "concert", "abstract", "acoustic"]

        for style in styles:
            keyframes = audio_sync_engine.generate_keyframes(
                sample_audio_features, style=style
            )
            assert len(keyframes) > 0


class TestGetStyleParams:
    """Tests for _get_style_params method."""

    @pytest.mark.unit
    def test_get_style_params_guitar_hero(self, audio_sync_engine):
        """Test guitar_hero style parameters."""
        params = audio_sync_engine._get_style_params("guitar_hero")

        assert "base_zoom" in params
        assert "beat_zoom" in params
        assert "base_angle" in params
        assert "onset_angle" in params
        assert params["motion_scale"] == 1.5 or "motion_scale" not in params

    @pytest.mark.unit
    def test_get_style_params_abstract(self, audio_sync_engine):
        """Test abstract style has higher motion."""
        abstract = audio_sync_engine._get_style_params("abstract")
        acoustic = audio_sync_engine._get_style_params("acoustic")

        # Abstract should have higher motion than acoustic
        assert abstract["onset_angle"] > acoustic["onset_angle"]

    @pytest.mark.unit
    def test_get_style_params_unknown(self, audio_sync_engine):
        """Test that unknown style falls back to guitar_hero."""
        params = audio_sync_engine._get_style_params("unknown_style")
        guitar_hero = audio_sync_engine._get_style_params("guitar_hero")

        assert params == guitar_hero


class TestInterpolateAtTime:
    """Tests for _interpolate_at_time method."""

    @pytest.mark.unit
    def test_interpolate_at_time_start(self, audio_sync_engine):
        """Test interpolation at start of curve."""
        curve = np.linspace(0, 1, 100)
        value = audio_sync_engine._interpolate_at_time(curve, 0.0, 10.0)

        assert value == pytest.approx(0.0, abs=0.02)

    @pytest.mark.unit
    def test_interpolate_at_time_end(self, audio_sync_engine):
        """Test interpolation at end of curve."""
        curve = np.linspace(0, 1, 100)
        value = audio_sync_engine._interpolate_at_time(curve, 10.0, 10.0)

        assert value == pytest.approx(1.0, abs=0.02)

    @pytest.mark.unit
    def test_interpolate_at_time_middle(self, audio_sync_engine):
        """Test interpolation in middle of curve."""
        curve = np.linspace(0, 1, 100)
        value = audio_sync_engine._interpolate_at_time(curve, 5.0, 10.0)

        assert value == pytest.approx(0.5, abs=0.1)

    @pytest.mark.unit
    def test_interpolate_empty_curve(self, audio_sync_engine):
        """Test interpolation with empty curve."""
        curve = np.array([])
        value = audio_sync_engine._interpolate_at_time(curve, 5.0, 10.0)

        assert value == 0.0


class TestBeatIntensity:
    """Tests for _beat_intensity method."""

    @pytest.mark.unit
    def test_beat_intensity_on_beat(self, audio_sync_engine):
        """Test intensity exactly on a beat."""
        beat_times = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
        intensity = audio_sync_engine._beat_intensity(0.5, beat_times)

        assert intensity == 1.0

    @pytest.mark.unit
    def test_beat_intensity_between_beats(self, audio_sync_engine):
        """Test intensity between beats."""
        beat_times = np.array([0.0, 1.0])
        intensity = audio_sync_engine._beat_intensity(0.5, beat_times)

        # 0.5s from nearest beat (at 0.0 or 1.0)
        # With decay_time=0.1, should be 0
        assert intensity == 0.0

    @pytest.mark.unit
    def test_beat_intensity_near_beat(self, audio_sync_engine):
        """Test intensity near a beat."""
        beat_times = np.array([0.0, 1.0])
        intensity = audio_sync_engine._beat_intensity(0.05, beat_times)

        # 0.05s from beat, decay_time=0.1
        assert 0.4 <= intensity <= 0.6

    @pytest.mark.unit
    def test_beat_intensity_no_beats(self, audio_sync_engine):
        """Test intensity with no beats."""
        beat_times = np.array([])
        intensity = audio_sync_engine._beat_intensity(0.5, beat_times)

        assert intensity == 0.0


class TestOnsetIntensity:
    """Tests for _onset_intensity method."""

    @pytest.mark.unit
    def test_onset_intensity_on_onset(self, audio_sync_engine):
        """Test intensity exactly on an onset."""
        onset_times = np.array([0.0, 0.5, 1.0])
        onset_strengths = np.array([1.0, 0.8, 0.6])

        intensity, strength = audio_sync_engine._onset_intensity(
            0.5, onset_times, onset_strengths
        )

        assert intensity == 1.0
        assert strength == 0.8

    @pytest.mark.unit
    def test_onset_intensity_no_onsets(self, audio_sync_engine):
        """Test intensity with no onsets."""
        intensity, strength = audio_sync_engine._onset_intensity(
            0.5, np.array([]), np.array([])
        )

        assert intensity == 0.0
        assert strength == 0.0


class TestExportDeforumSchedule:
    """Tests for export_deforum_schedule method."""

    @pytest.mark.unit
    def test_export_schedule_basic(self, audio_sync_engine, sample_keyframes):
        """Test basic schedule export."""
        schedule = audio_sync_engine.export_deforum_schedule(sample_keyframes)

        assert isinstance(schedule, dict)
        assert "zoom" in schedule
        assert "angle" in schedule
        assert "translation_x" in schedule
        assert "translation_y" in schedule
        assert "strength_schedule" in schedule

    @pytest.mark.unit
    def test_export_schedule_format(self, audio_sync_engine, sample_keyframes):
        """Test that schedule has correct format."""
        schedule = audio_sync_engine.export_deforum_schedule(sample_keyframes)

        # Should be comma-separated frame:value pairs
        zoom_entries = schedule["zoom"].split(", ")
        assert len(zoom_entries) == len(sample_keyframes)

        # Each entry should have format "frame:(value)"
        for entry in zoom_entries:
            assert ":" in entry
            assert "(" in entry
            assert ")" in entry

    @pytest.mark.unit
    def test_export_schedule_empty(self, audio_sync_engine):
        """Test export with empty keyframes."""
        schedule = audio_sync_engine.export_deforum_schedule([])

        assert schedule["zoom"] == ""
        assert schedule["angle"] == ""
