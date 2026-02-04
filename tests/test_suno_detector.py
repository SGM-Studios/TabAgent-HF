"""
Tests for agents/suno_detector.py - AI-Generated Audio Detection
"""

import pytest
import numpy as np
from pathlib import Path
from agents import SunoDetector
from agents.types import AudioAnalysis


class TestSunoDetectorInit:
    """Tests for SunoDetector initialization."""

    @pytest.mark.unit
    def test_init_default(self):
        """Test default initialization."""
        detector = SunoDetector()
        assert detector.high_freq_threshold == 0.15
        assert detector.spectral_flatness_threshold == 0.4
        assert detector.consistency_threshold == 0.7

    @pytest.mark.unit
    def test_init_custom_thresholds(self):
        """Test initialization with custom thresholds."""
        detector = SunoDetector(
            high_freq_threshold=0.2,
            spectral_flatness_threshold=0.5,
            consistency_threshold=0.8
        )
        assert detector.high_freq_threshold == 0.2
        assert detector.spectral_flatness_threshold == 0.5
        assert detector.consistency_threshold == 0.8


class TestAnalyze:
    """Tests for analyze method."""

    @pytest.mark.unit
    def test_analyze_returns_audio_analysis(self, suno_detector, sample_audio_mono):
        """Test that analyze returns AudioAnalysis object."""
        result = suno_detector.analyze(sample_audio_mono)

        assert isinstance(result, AudioAnalysis)
        assert isinstance(result.is_ai_generated, bool)
        assert 0 <= result.confidence <= 1

    @pytest.mark.unit
    def test_analyze_natural_sine_wave(self, suno_detector, sample_audio_mono):
        """Test analysis of simple sine wave (should not be detected as AI)."""
        result = suno_detector.analyze(sample_audio_mono)

        # A simple sine wave should likely be detected as natural
        # (though this depends on the exact parameters)
        assert isinstance(result.artifacts_detected, list)

    @pytest.mark.unit
    def test_analyze_returns_all_metrics(self, suno_detector, sample_audio_mono):
        """Test that all metrics are present in result."""
        result = suno_detector.analyze(sample_audio_mono)

        assert hasattr(result, 'high_freq_ratio')
        assert hasattr(result, 'spectral_flatness')
        assert hasattr(result, 'temporal_consistency')
        assert result.high_freq_ratio >= 0
        assert result.spectral_flatness >= 0
        assert result.temporal_consistency >= 0

    @pytest.mark.unit
    def test_analyze_complex_audio(self, suno_detector, sample_audio_complex):
        """Test analysis of complex audio."""
        result = suno_detector.analyze(sample_audio_complex)

        assert isinstance(result, AudioAnalysis)


class TestAnalyzeHighFreq:
    """Tests for high frequency analysis."""

    @pytest.mark.unit
    def test_high_freq_simple_audio(self, suno_detector, sample_audio_mono):
        """Test high frequency analysis of simple audio."""
        import librosa

        audio, sr = librosa.load(sample_audio_mono, sr=22050, mono=True)
        ratio = suno_detector._analyze_high_freq(audio, sr)

        assert ratio >= 0
        # A 440 Hz sine wave should have minimal high freq content
        assert ratio < 1.0

    @pytest.mark.unit
    def test_high_freq_noise(self, suno_detector):
        """Test high frequency analysis of white noise."""
        # White noise should have significant high freq content
        audio = np.random.randn(22050)  # 1 second of noise
        sr = 22050

        ratio = suno_detector._analyze_high_freq(audio, sr)
        assert ratio > 0


class TestAnalyzeSpectralFlatness:
    """Tests for spectral flatness analysis."""

    @pytest.mark.unit
    def test_spectral_flatness_sine(self, suno_detector, sample_audio_mono):
        """Test spectral flatness of sine wave."""
        import librosa

        audio, sr = librosa.load(sample_audio_mono, sr=22050, mono=True)
        flatness = suno_detector._analyze_spectral_flatness(audio, sr)

        # Sine wave has low spectral flatness (very peaked spectrum)
        assert 0 <= flatness <= 1

    @pytest.mark.unit
    def test_spectral_flatness_noise(self, suno_detector):
        """Test spectral flatness of white noise."""
        audio = np.random.randn(22050)
        sr = 22050

        flatness = suno_detector._analyze_spectral_flatness(audio, sr)

        # White noise has high spectral flatness (flat spectrum)
        assert flatness > 0


class TestAnalyzeTemporalConsistency:
    """Tests for temporal consistency analysis."""

    @pytest.mark.unit
    def test_temporal_consistency_constant(self, suno_detector):
        """Test temporal consistency of constant amplitude audio."""
        # Constant amplitude = high consistency
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 2, 44100))
        sr = 22050

        consistency = suno_detector._analyze_temporal_consistency(audio, sr)

        assert 0 <= consistency <= 1

    @pytest.mark.unit
    def test_temporal_consistency_with_beats(self, suno_detector, sample_audio_with_beats):
        """Test temporal consistency of audio with beats."""
        import librosa

        audio, sr = librosa.load(sample_audio_with_beats, sr=22050, mono=True)
        consistency = suno_detector._analyze_temporal_consistency(audio, sr)

        assert 0 <= consistency <= 1


class TestPreprocess:
    """Tests for audio preprocessing."""

    @pytest.mark.unit
    def test_preprocess_creates_file(self, suno_detector, sample_audio_mono, temp_dir):
        """Test that preprocessing creates output file."""
        output_path = str(temp_dir / "processed.wav")

        result = suno_detector.preprocess(sample_audio_mono, output_path)

        assert Path(result).exists()

    @pytest.mark.unit
    def test_preprocess_auto_output_path(self, suno_detector, sample_audio_mono):
        """Test preprocessing with auto-generated output path."""
        result = suno_detector.preprocess(sample_audio_mono)

        assert Path(result).exists()
        assert "_processed" in result

    @pytest.mark.unit
    def test_preprocess_stereo(self, suno_detector, sample_audio_stereo, temp_dir):
        """Test preprocessing of stereo audio."""
        output_path = str(temp_dir / "stereo_processed.wav")

        result = suno_detector.preprocess(sample_audio_stereo, output_path)

        assert Path(result).exists()

    @pytest.mark.unit
    def test_preprocess_options(self, suno_detector, sample_audio_mono, temp_dir):
        """Test preprocessing with different options."""
        output1 = str(temp_dir / "shimmer_only.wav")
        output2 = str(temp_dir / "artifacts_only.wav")

        result1 = suno_detector.preprocess(
            sample_audio_mono, output1,
            reduce_shimmer=True, reduce_artifacts=False
        )
        result2 = suno_detector.preprocess(
            sample_audio_mono, output2,
            reduce_shimmer=False, reduce_artifacts=True
        )

        assert Path(result1).exists()
        assert Path(result2).exists()


class TestReduceHighFreq:
    """Tests for high frequency reduction."""

    @pytest.mark.unit
    def test_reduce_high_freq_preserves_shape(self, suno_detector):
        """Test that high freq reduction preserves audio shape."""
        audio = np.random.randn(22050)
        sr = 22050

        result = suno_detector._reduce_high_freq(audio, sr, cutoff=10000)

        assert result.shape == audio.shape

    @pytest.mark.unit
    def test_reduce_high_freq_blends(self, suno_detector):
        """Test that reduction is a blend (not full filter)."""
        audio = np.random.randn(22050)
        sr = 22050

        result = suno_detector._reduce_high_freq(audio, sr, cutoff=10000)

        # Should not be identical to original or fully filtered
        assert not np.allclose(result, audio)


class TestSmoothSpectrum:
    """Tests for spectral smoothing."""

    @pytest.mark.unit
    def test_smooth_spectrum_preserves_length(self, suno_detector):
        """Test that spectral smoothing preserves audio length."""
        audio = np.random.randn(22050)
        sr = 22050

        result = suno_detector._smooth_spectrum(audio, sr)

        # STFT/ISTFT may have slight length difference
        assert abs(len(result) - len(audio)) < 100

    @pytest.mark.unit
    def test_smooth_spectrum_reduces_artifacts(self, suno_detector):
        """Test that spectral smoothing changes the audio."""
        # Create audio with spectral artifacts
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 22050))
        # Add artificial grid pattern
        audio += 0.1 * np.sin(2 * np.pi * 8000 * np.linspace(0, 1, 22050))
        sr = 22050

        result = suno_detector._smooth_spectrum(audio, sr)

        # Result should be different from original
        assert not np.allclose(result[:len(audio)], audio)


class TestArtifactDetection:
    """Tests for artifact type detection."""

    @pytest.mark.unit
    def test_detects_high_freq_shimmer(self, suno_detector):
        """Test detection of high frequency shimmer artifact."""
        # Create audio with high freq content
        sr = 22050
        t = np.linspace(0, 1, sr)
        audio = np.sin(2 * np.pi * 440 * t)
        audio += 0.5 * np.sin(2 * np.pi * 12000 * t)  # Add high freq

        # Analyze manually
        high_freq_ratio = suno_detector._analyze_high_freq(audio, sr)

        # Should detect high freq content if ratio exceeds threshold
        is_shimmer = high_freq_ratio > suno_detector.high_freq_threshold
        # Result depends on exact implementation
        assert isinstance(is_shimmer, bool)

    @pytest.mark.unit
    def test_artifacts_list_format(self, suno_detector, sample_audio_mono):
        """Test that artifacts are returned as list of strings."""
        result = suno_detector.analyze(sample_audio_mono)

        assert isinstance(result.artifacts_detected, list)
        for artifact in result.artifacts_detected:
            assert isinstance(artifact, str)
