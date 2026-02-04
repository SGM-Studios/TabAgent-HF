"""
Tests for deforum/generator.py - DeforumGenerator
"""

import pytest
import numpy as np
from pathlib import Path
from PIL import Image
from deforum import DeforumGenerator
from deforum.types import VideoResult


class TestDeforumGeneratorInit:
    """Tests for DeforumGenerator initialization."""

    @pytest.mark.unit
    def test_init_default(self):
        """Test default initialization."""
        generator = DeforumGenerator()
        assert generator.model_id == "runwayml/stable-diffusion-v1-5"
        assert generator.width == 512
        assert generator.height == 512
        assert generator.fps == 15
        assert generator._model_loaded is False

    @pytest.mark.unit
    def test_init_custom(self):
        """Test initialization with custom parameters."""
        generator = DeforumGenerator(
            model_id="test/model",
            width=768,
            height=512,
            fps=30
        )
        assert generator.model_id == "test/model"
        assert generator.width == 768
        assert generator.height == 512
        assert generator.fps == 30

    @pytest.mark.unit
    def test_init_creates_audio_sync(self):
        """Test that initialization creates AudioSyncEngine."""
        generator = DeforumGenerator(fps=20)
        assert generator.audio_sync.fps == 20


class TestDeviceDetection:
    """Tests for device detection."""

    @pytest.mark.unit
    def test_detect_device_explicit(self):
        """Test explicit device selection."""
        generator = DeforumGenerator(device="cpu")
        assert generator.device == "cpu"

    @pytest.mark.unit
    def test_detect_device_auto(self):
        """Test auto device detection."""
        generator = DeforumGenerator(device="auto")
        assert generator.device in ["cpu", "cuda"]


class TestGeneratePlaceholder:
    """Tests for placeholder video generation."""

    @pytest.mark.unit
    def test_generate_placeholder(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test placeholder video generation."""
        output_path = str(temp_dir / "placeholder.mp4")

        result = deforum_generator._generate_placeholder(
            sample_audio_mono, output_path, max_frames=30
        )

        assert isinstance(result, VideoResult)
        assert result.style == "placeholder"
        assert Path(result.video_path).exists()

    @pytest.mark.unit
    def test_generate_placeholder_auto_path(self, deforum_generator, sample_audio_mono):
        """Test placeholder with auto-generated path."""
        result = deforum_generator._generate_placeholder(
            sample_audio_mono, None, max_frames=30
        )

        assert result is not None
        assert Path(result.video_path).exists()

    @pytest.mark.unit
    def test_generate_placeholder_max_frames(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test that placeholder respects max_frames."""
        output_path = str(temp_dir / "placeholder.mp4")

        result = deforum_generator._generate_placeholder(
            sample_audio_mono, output_path, max_frames=20
        )

        assert result.frames_generated <= 20


class TestWarpImage:
    """Tests for image warping."""

    @pytest.mark.unit
    def test_warp_image_zoom(self, deforum_generator):
        """Test image warping with zoom."""
        from deforum.types import AnimationKeyframe

        image = Image.new('RGB', (512, 512), color='blue')
        kf = AnimationKeyframe(frame=0, time=0.0, zoom=1.5)

        warped = deforum_generator._warp_image(image, kf)

        assert isinstance(warped, Image.Image)
        assert warped.size == image.size

    @pytest.mark.unit
    def test_warp_image_rotation(self, deforum_generator):
        """Test image warping with rotation."""
        from deforum.types import AnimationKeyframe

        image = Image.new('RGB', (512, 512), color='blue')
        kf = AnimationKeyframe(frame=0, time=0.0, angle=45.0)

        warped = deforum_generator._warp_image(image, kf)

        assert isinstance(warped, Image.Image)

    @pytest.mark.unit
    def test_warp_image_translation(self, deforum_generator):
        """Test image warping with translation."""
        from deforum.types import AnimationKeyframe

        image = Image.new('RGB', (512, 512), color='blue')
        kf = AnimationKeyframe(frame=0, time=0.0, translation_x=50, translation_y=30)

        warped = deforum_generator._warp_image(image, kf)

        assert isinstance(warped, Image.Image)


class TestAddNoise:
    """Tests for noise addition."""

    @pytest.mark.unit
    def test_add_noise_changes_image(self, deforum_generator):
        """Test that noise changes the image."""
        image = Image.new('RGB', (512, 512), color='blue')
        noisy = deforum_generator._add_noise(image, amount=0.5)

        # Convert to numpy for comparison
        orig_arr = np.array(image)
        noisy_arr = np.array(noisy)

        # Should not be identical
        assert not np.array_equal(orig_arr, noisy_arr)

    @pytest.mark.unit
    def test_add_noise_preserves_size(self, deforum_generator):
        """Test that noise preserves image size."""
        image = Image.new('RGB', (512, 512), color='blue')
        noisy = deforum_generator._add_noise(image, amount=0.3)

        assert noisy.size == image.size

    @pytest.mark.unit
    def test_add_noise_amount(self, deforum_generator):
        """Test noise amount affects variance."""
        image = Image.new('RGB', (512, 512), color=(128, 128, 128))

        noisy_low = deforum_generator._add_noise(image, amount=0.1)
        noisy_high = deforum_generator._add_noise(image, amount=0.5)

        # Higher noise should have more variance
        var_low = np.var(np.array(noisy_low))
        var_high = np.var(np.array(noisy_high))

        assert var_high > var_low


class TestCompileVideo:
    """Tests for video compilation."""

    @pytest.mark.unit
    def test_compile_video_creates_file(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test that compile_video creates output file."""
        # Create simple frames
        frames = [
            Image.new('RGB', (512, 512), color=(i * 10, i * 10, i * 10))
            for i in range(10)
        ]

        output_path = str(temp_dir / "compiled.mp4")
        result = deforum_generator._compile_video(frames, sample_audio_mono, output_path)

        assert Path(result).exists()

    @pytest.mark.unit
    def test_compile_video_with_audio(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test video compilation with audio."""
        frames = [
            Image.new('RGB', (512, 512), color=(i * 10, i * 10, i * 10))
            for i in range(10)
        ]

        output_path = str(temp_dir / "with_audio.mp4")
        result = deforum_generator._compile_video(frames, sample_audio_mono, output_path)

        assert Path(result).exists()
        # File size should be larger with audio
        assert Path(result).stat().st_size > 0


class TestGenerate:
    """Tests for main generate method."""

    @pytest.mark.unit
    def test_generate_without_model(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test generation without loaded model (uses placeholder)."""
        output_path = str(temp_dir / "output.mp4")

        result = deforum_generator.generate(
            sample_audio_mono,
            output_path=output_path,
            max_frames=20
        )

        assert isinstance(result, VideoResult)
        assert Path(result.video_path).exists()

    @pytest.mark.unit
    def test_generate_respects_max_frames(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test that generate respects max_frames."""
        output_path = str(temp_dir / "limited.mp4")

        result = deforum_generator.generate(
            sample_audio_mono,
            output_path=output_path,
            max_frames=15
        )

        assert result.frames_generated <= 15

    @pytest.mark.unit
    def test_generate_auto_output_path(self, deforum_generator, sample_audio_mono):
        """Test generation with auto output path."""
        result = deforum_generator.generate(
            sample_audio_mono,
            max_frames=10
        )

        assert result is not None
        # Output path should be based on input


class TestVideoResult:
    """Tests for VideoResult properties."""

    @pytest.mark.unit
    def test_video_result_properties(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test VideoResult has correct properties."""
        output_path = str(temp_dir / "test.mp4")

        result = deforum_generator.generate(
            sample_audio_mono,
            output_path=output_path,
            style="guitar_hero",
            max_frames=20
        )

        assert result.fps == deforum_generator.fps
        assert result.duration_seconds == result.frames_generated / result.fps

    @pytest.mark.unit
    def test_video_result_style(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test that VideoResult records style."""
        result = deforum_generator.generate(
            sample_audio_mono,
            style="abstract",
            max_frames=10
        )

        # In placeholder mode, style is "placeholder"
        # In actual mode, should be "abstract"
        assert result.style in ["abstract", "placeholder"]


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.unit
    def test_very_short_audio(self, deforum_generator, temp_dir):
        """Test with very short audio."""
        import soundfile as sf

        sr = 22050
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, int(sr * 0.5)))

        audio_path = temp_dir / "short.wav"
        sf.write(str(audio_path), audio, sr)

        result = deforum_generator.generate(
            str(audio_path),
            max_frames=30
        )

        assert result is not None

    @pytest.mark.unit
    def test_custom_prompt(self, deforum_generator, sample_audio_mono, temp_dir):
        """Test generation with custom prompt."""
        result = deforum_generator.generate(
            sample_audio_mono,
            prompt="custom test prompt",
            max_frames=10
        )

        assert result is not None
