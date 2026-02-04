"""
Tests for agents/splitter.py - SplitterAgent (Stem Separation)
"""

import pytest
import numpy as np
from pathlib import Path
from agents import SplitterAgent


class TestSplitterAgentInit:
    """Tests for SplitterAgent initialization."""

    @pytest.mark.unit
    def test_init_default(self, temp_dir):
        """Test default initialization."""
        agent = SplitterAgent(output_dir=str(temp_dir))
        assert agent.output_dir == temp_dir

    @pytest.mark.unit
    def test_init_creates_directory(self, temp_dir):
        """Test that init creates output directory."""
        output = temp_dir / "new_stems"
        agent = SplitterAgent(output_dir=str(output))

        assert output.exists()

    @pytest.mark.unit
    def test_init_nested_directory(self, temp_dir):
        """Test that init creates nested directories."""
        output = temp_dir / "a" / "b" / "stems"
        agent = SplitterAgent(output_dir=str(output))

        assert output.exists()


class TestProcessGuitars:
    """Tests for mid-side guitar processing."""

    @pytest.mark.unit
    def test_process_guitars_stereo(self, splitter_agent, sample_audio_stereo):
        """Test guitar processing with stereo audio."""
        result = splitter_agent.process_guitars(sample_audio_stereo)

        assert "lead" in result
        assert "left" in result
        assert "right" in result

        # Check files exist
        assert Path(result["lead"]).exists()
        assert Path(result["left"]).exists()
        assert Path(result["right"]).exists()

    @pytest.mark.unit
    def test_process_guitars_mono(self, splitter_agent, sample_audio_mono):
        """Test guitar processing with mono audio."""
        result = splitter_agent.process_guitars(sample_audio_mono)

        assert "lead" in result
        assert "left" in result
        assert "right" in result

    @pytest.mark.unit
    def test_process_guitars_output_format(self, splitter_agent, sample_audio_stereo):
        """Test that guitar processing outputs WAV files."""
        result = splitter_agent.process_guitars(sample_audio_stereo)

        for key, path in result.items():
            assert path.endswith(".wav")

    @pytest.mark.unit
    def test_process_guitars_normalized(self, splitter_agent, sample_audio_stereo):
        """Test that processed audio is normalized."""
        import soundfile as sf

        result = splitter_agent.process_guitars(sample_audio_stereo)

        for key, path in result.items():
            audio, sr = sf.read(path)
            # Should be normalized to peak <= 0.9
            assert np.max(np.abs(audio)) <= 0.95


class TestProcessBass:
    """Tests for bass processing."""

    @pytest.mark.unit
    def test_process_bass_returns_path(self, splitter_agent, sample_audio_mono):
        """Test that bass processing returns a path."""
        result = splitter_agent.process_bass(sample_audio_mono)

        assert isinstance(result, str)
        assert Path(result).exists()

    @pytest.mark.unit
    def test_process_bass_output_format(self, splitter_agent, sample_audio_mono):
        """Test that bass processing outputs WAV file."""
        result = splitter_agent.process_bass(sample_audio_mono)

        assert result.endswith(".wav")
        assert "_clean" in result

    @pytest.mark.unit
    def test_process_bass_normalized(self, splitter_agent, sample_audio_mono):
        """Test that processed bass is normalized."""
        import soundfile as sf

        result = splitter_agent.process_bass(sample_audio_mono)

        audio, sr = sf.read(result)
        assert np.max(np.abs(audio)) <= 0.95

    @pytest.mark.unit
    def test_process_bass_stereo_to_mono(self, splitter_agent, sample_audio_stereo):
        """Test that stereo bass is converted to mono."""
        import soundfile as sf

        result = splitter_agent.process_bass(sample_audio_stereo)

        audio, sr = sf.read(result)
        # Should be mono (1D array)
        assert audio.ndim == 1


class TestSeparateStems:
    """Tests for Demucs stem separation (may be mocked in CI)."""

    @pytest.mark.unit
    def test_separate_stems_fallback(self, splitter_agent, sample_audio_mono):
        """Test that stem separation falls back gracefully when Demucs unavailable."""
        # This tests the fallback behavior when Demucs isn't installed
        result = splitter_agent.separate_stems(sample_audio_mono)

        assert "guitar" in result
        assert "bass" in result
        assert "original" in result

        # In fallback mode, all stems point to original
        # (actual Demucs separation requires the full model)

    @pytest.mark.unit
    def test_separate_stems_returns_dict(self, splitter_agent, sample_audio_mono):
        """Test that stem separation returns a dictionary."""
        result = splitter_agent.separate_stems(sample_audio_mono)

        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_separate_stems_keys(self, splitter_agent, sample_audio_mono):
        """Test that stem separation returns required keys."""
        result = splitter_agent.separate_stems(sample_audio_mono)

        assert "guitar" in result
        assert "bass" in result


class TestMidSideProcessing:
    """Tests for mid-side audio processing algorithm."""

    @pytest.mark.unit
    def test_mid_extracts_center(self, splitter_agent, temp_dir):
        """Test that mid channel extracts center content."""
        import soundfile as sf

        # Create stereo audio with identical L/R (all center)
        sr = 22050
        t = np.linspace(0, 1, sr)
        mono = np.sin(2 * np.pi * 440 * t)
        stereo = np.vstack([mono, mono]).T

        test_file = temp_dir / "center_test.wav"
        sf.write(str(test_file), stereo, sr)

        result = splitter_agent.process_guitars(str(test_file))

        # Lead (mid) should contain most content
        lead_audio, _ = sf.read(result["lead"])
        assert np.max(np.abs(lead_audio)) > 0.5

    @pytest.mark.unit
    def test_side_extracts_width(self, splitter_agent, temp_dir):
        """Test that side channels extract width content."""
        import soundfile as sf

        sr = 22050
        t = np.linspace(0, 1, sr)

        # Left-only content
        left = np.sin(2 * np.pi * 440 * t)
        right = np.zeros_like(left)
        stereo = np.vstack([left, right]).T

        test_file = temp_dir / "width_test.wav"
        sf.write(str(test_file), stereo, sr)

        result = splitter_agent.process_guitars(str(test_file))

        # Left rhythm should contain the content
        left_audio, _ = sf.read(result["left"])
        assert np.max(np.abs(left_audio)) > 0.1


class TestFrequencyFiltering:
    """Tests for bass frequency filtering."""

    @pytest.mark.unit
    def test_filter_preserves_low_freq(self, splitter_agent, temp_dir):
        """Test that filtering preserves low frequencies."""
        import soundfile as sf

        sr = 22050
        t = np.linspace(0, 1, sr)

        # Low frequency content (bass note)
        low_freq = np.sin(2 * np.pi * 82 * t)  # E2

        test_file = temp_dir / "low_freq_test.wav"
        sf.write(str(test_file), low_freq, sr)

        result = splitter_agent.process_bass(str(test_file))

        # Should preserve most energy
        processed, _ = sf.read(result)
        original_energy = np.sum(low_freq ** 2)
        processed_energy = np.sum(processed ** 2)

        # Should retain significant energy
        assert processed_energy > original_energy * 0.5

    @pytest.mark.unit
    def test_filter_reduces_high_freq(self, splitter_agent, temp_dir):
        """Test that filtering reduces high frequencies."""
        import soundfile as sf

        sr = 22050
        t = np.linspace(0, 1, sr)

        # High frequency content (fret noise)
        high_freq = np.sin(2 * np.pi * 5000 * t)

        test_file = temp_dir / "high_freq_test.wav"
        sf.write(str(test_file), high_freq, sr)

        result = splitter_agent.process_bass(str(test_file))

        # Should reduce energy
        processed, _ = sf.read(result)
        original_energy = np.sum(high_freq ** 2)
        processed_energy = np.sum(processed ** 2)

        # Should have less energy after filtering
        assert processed_energy < original_energy


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.unit
    def test_very_short_audio(self, splitter_agent, temp_dir):
        """Test processing very short audio."""
        import soundfile as sf

        sr = 22050
        # 0.1 seconds of audio
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, int(sr * 0.1)))

        test_file = temp_dir / "short.wav"
        sf.write(str(test_file), audio, sr)

        result = splitter_agent.process_bass(str(test_file))
        assert Path(result).exists()

    @pytest.mark.unit
    def test_silent_audio(self, splitter_agent, temp_dir):
        """Test processing silent audio."""
        import soundfile as sf

        sr = 22050
        audio = np.zeros(sr)  # 1 second of silence

        test_file = temp_dir / "silent.wav"
        sf.write(str(test_file), audio, sr)

        result = splitter_agent.process_bass(str(test_file))
        assert Path(result).exists()

        # Output should also be silent
        processed, _ = sf.read(result)
        assert np.max(np.abs(processed)) < 0.01
