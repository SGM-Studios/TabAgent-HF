"""
Tests for deforum/types.py - Deforum Type Definitions
"""

import pytest
import numpy as np
from deforum.types import (
    AudioFeatures,
    AnimationKeyframe,
    VideoResult,
    StylePreset,
    GenerationConfig,
    MotionParams,
)


class TestAudioFeatures:
    """Tests for AudioFeatures dataclass."""

    @pytest.mark.unit
    def test_audio_features_creation(self):
        """Test basic AudioFeatures creation."""
        features = AudioFeatures(
            duration=5.0,
            bpm=120.0,
            beat_times=np.array([0.0, 0.5, 1.0]),
            onset_times=np.array([0.0, 0.25, 0.5]),
            onset_strengths=np.array([1.0, 0.5, 0.8]),
            rms_curve=np.linspace(0, 1, 100),
            spectral_curve=np.random.rand(100),
            sample_rate=22050
        )

        assert features.duration == 5.0
        assert features.bpm == 120.0
        assert features.sample_rate == 22050

    @pytest.mark.unit
    def test_audio_features_invalid_duration(self):
        """Test that non-positive duration raises error."""
        with pytest.raises(ValueError, match="Duration must be positive"):
            AudioFeatures(
                duration=0.0,
                bpm=120.0,
                beat_times=np.array([]),
                onset_times=np.array([]),
                onset_strengths=np.array([]),
                rms_curve=np.array([]),
                spectral_curve=np.array([]),
                sample_rate=22050
            )

    @pytest.mark.unit
    def test_audio_features_invalid_bpm(self):
        """Test that non-positive BPM raises error."""
        with pytest.raises(ValueError, match="BPM must be positive"):
            AudioFeatures(
                duration=5.0,
                bpm=-120.0,
                beat_times=np.array([]),
                onset_times=np.array([]),
                onset_strengths=np.array([]),
                rms_curve=np.array([]),
                spectral_curve=np.array([]),
                sample_rate=22050
            )

    @pytest.mark.unit
    def test_audio_features_invalid_sample_rate(self):
        """Test that non-positive sample rate raises error."""
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            AudioFeatures(
                duration=5.0,
                bpm=120.0,
                beat_times=np.array([]),
                onset_times=np.array([]),
                onset_strengths=np.array([]),
                rms_curve=np.array([]),
                spectral_curve=np.array([]),
                sample_rate=0
            )


class TestAnimationKeyframe:
    """Tests for AnimationKeyframe dataclass."""

    @pytest.mark.unit
    def test_keyframe_creation(self):
        """Test basic keyframe creation."""
        kf = AnimationKeyframe(
            frame=0,
            time=0.0,
            zoom=1.05,
            angle=5.0,
            translation_x=10.0,
            translation_y=5.0,
            strength=0.65,
            prompt_weight=1.0
        )

        assert kf.frame == 0
        assert kf.zoom == 1.05
        assert kf.angle == 5.0

    @pytest.mark.unit
    def test_keyframe_defaults(self):
        """Test keyframe default values."""
        kf = AnimationKeyframe(frame=0, time=0.0)

        assert kf.zoom == 1.0
        assert kf.angle == 0.0
        assert kf.translation_x == 0.0
        assert kf.translation_y == 0.0
        assert kf.strength == 0.65
        assert kf.prompt_weight == 1.0

    @pytest.mark.unit
    def test_keyframe_invalid_frame(self):
        """Test that negative frame raises error."""
        with pytest.raises(ValueError, match="Frame must be non-negative"):
            AnimationKeyframe(frame=-1, time=0.0)

    @pytest.mark.unit
    def test_keyframe_invalid_time(self):
        """Test that negative time raises error."""
        with pytest.raises(ValueError, match="Time must be non-negative"):
            AnimationKeyframe(frame=0, time=-1.0)

    @pytest.mark.unit
    def test_keyframe_invalid_strength_high(self):
        """Test that strength > 1 raises error."""
        with pytest.raises(ValueError, match="Strength must be 0-1"):
            AnimationKeyframe(frame=0, time=0.0, strength=1.5)

    @pytest.mark.unit
    def test_keyframe_invalid_strength_low(self):
        """Test that strength < 0 raises error."""
        with pytest.raises(ValueError, match="Strength must be 0-1"):
            AnimationKeyframe(frame=0, time=0.0, strength=-0.1)


class TestVideoResult:
    """Tests for VideoResult dataclass."""

    @pytest.mark.unit
    def test_video_result_creation(self, temp_dir):
        """Test basic VideoResult creation."""
        video_path = str(temp_dir / "test.mp4")
        # Create dummy file
        Path(video_path).touch()

        result = VideoResult(
            video_path=video_path,
            frames_generated=150,
            duration_seconds=10.0,
            fps=15,
            style="guitar_hero"
        )

        assert result.frames_generated == 150
        assert result.duration_seconds == 10.0
        assert result.fps == 15

    @pytest.mark.unit
    def test_video_result_file_size(self, temp_dir):
        """Test file_size_mb property."""
        video_path = temp_dir / "test.mp4"
        # Create file with some content
        video_path.write_bytes(b"0" * 1024 * 1024)  # 1 MB

        result = VideoResult(
            video_path=str(video_path),
            frames_generated=150,
            duration_seconds=10.0,
            fps=15,
            style="guitar_hero"
        )

        size = result.file_size_mb
        assert size is not None
        assert 0.9 <= size <= 1.1  # Approximately 1 MB

    @pytest.mark.unit
    def test_video_result_file_size_missing(self):
        """Test file_size_mb when file doesn't exist."""
        result = VideoResult(
            video_path="/nonexistent/path.mp4",
            frames_generated=150,
            duration_seconds=10.0,
            fps=15,
            style="guitar_hero"
        )

        assert result.file_size_mb is None


class TestStylePreset:
    """Tests for StylePreset dataclass."""

    @pytest.mark.unit
    def test_style_preset_creation(self):
        """Test basic StylePreset creation."""
        preset = StylePreset(
            name="Test Style",
            description="A test style",
            prompt_base="abstract art, colorful",
            negative_prompt="blurry, dark",
            color_coherence="LAB",
            motion_scale=1.5,
            strength_base=0.6,
            guidance_scale=7.5
        )

        assert preset.name == "Test Style"
        assert preset.motion_scale == 1.5

    @pytest.mark.unit
    def test_style_preset_defaults(self):
        """Test StylePreset default values."""
        preset = StylePreset(
            name="Test",
            description="Test",
            prompt_base="test prompt"
        )

        assert preset.negative_prompt == "blurry, low quality, deformed"
        assert preset.color_coherence == "LAB"
        assert preset.motion_scale == 1.0
        assert preset.strength_base == 0.65
        assert preset.guidance_scale == 7.5


class TestGenerationConfig:
    """Tests for GenerationConfig dataclass."""

    @pytest.mark.unit
    def test_config_creation(self):
        """Test basic GenerationConfig creation."""
        config = GenerationConfig(
            model_id="test/model",
            width=768,
            height=512,
            fps=30,
            max_frames=300,
            num_inference_steps=30,
            guidance_scale=8.0,
            seed=42
        )

        assert config.width == 768
        assert config.height == 512
        assert config.seed == 42

    @pytest.mark.unit
    def test_config_defaults(self):
        """Test GenerationConfig default values."""
        config = GenerationConfig()

        assert config.model_id == "runwayml/stable-diffusion-v1-5"
        assert config.width == 512
        assert config.height == 512
        assert config.fps == 15
        assert config.max_frames == 120
        assert config.num_inference_steps == 25
        assert config.guidance_scale == 7.5
        assert config.seed is None

    @pytest.mark.unit
    def test_config_invalid_dimensions(self):
        """Test that invalid dimensions raise error."""
        with pytest.raises(ValueError, match="Dimensions must be positive"):
            GenerationConfig(width=0, height=512)

        with pytest.raises(ValueError, match="Dimensions must be positive"):
            GenerationConfig(width=512, height=-1)

    @pytest.mark.unit
    def test_config_invalid_fps(self):
        """Test that invalid FPS raises error."""
        with pytest.raises(ValueError, match="FPS must be positive"):
            GenerationConfig(fps=0)

    @pytest.mark.unit
    def test_config_invalid_max_frames(self):
        """Test that invalid max_frames raises error."""
        with pytest.raises(ValueError, match="Max frames must be positive"):
            GenerationConfig(max_frames=0)


class TestMotionParams:
    """Tests for MotionParams dataclass."""

    @pytest.mark.unit
    def test_motion_params_creation(self):
        """Test basic MotionParams creation."""
        params = MotionParams(
            base_zoom=1.02,
            beat_zoom=0.08,
            base_angle=0.5,
            onset_angle=3.0
        )

        assert params.base_zoom == 1.02
        assert params.beat_zoom == 0.08

    @pytest.mark.unit
    def test_motion_params_defaults(self):
        """Test MotionParams default values."""
        params = MotionParams()

        assert params.base_zoom == 1.0
        assert params.beat_zoom == 0.05
        assert params.rms_zoom == 0.02
        assert params.base_angle == 0.0
        assert params.onset_angle == 2.0
        assert params.base_strength == 0.65


# Import Path for file operations
from pathlib import Path
