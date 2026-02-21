"""
Deforum - Shared Type Definitions
Centralized dataclasses and type definitions for the deforum module.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class AudioFeatures:
    """
    Extracted audio features for animation sync.

    Attributes:
        duration: Total duration in seconds
        bpm: Estimated beats per minute
        beat_times: Array of beat timestamps
        onset_times: Array of note onset timestamps
        onset_strengths: Array of onset strength values (normalized 0-1)
        rms_curve: RMS energy curve (normalized 0-1)
        spectral_curve: Spectral centroid curve (normalized 0-1)
        sample_rate: Audio sample rate used for analysis
    """
    duration: float
    bpm: float
    beat_times: np.ndarray
    onset_times: np.ndarray
    onset_strengths: np.ndarray
    rms_curve: np.ndarray
    spectral_curve: np.ndarray
    sample_rate: int

    def __post_init__(self):
        """Validate audio features."""
        if self.duration <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")
        if self.bpm <= 0:
            raise ValueError(f"BPM must be positive, got {self.bpm}")
        if self.sample_rate <= 0:
            raise ValueError(f"Sample rate must be positive, got {self.sample_rate}")


@dataclass
class AnimationKeyframe:
    """
    A keyframe for Deforum animation.

    Attributes:
        frame: Frame number
        time: Time in seconds
        zoom: Zoom factor (1.0 = no zoom)
        angle: Rotation angle in degrees
        translation_x: X translation in pixels
        translation_y: Y translation in pixels
        strength: Denoising strength for img2img (0.0-1.0)
        prompt_weight: Prompt influence weight
    """
    frame: int
    time: float
    zoom: float = 1.0
    angle: float = 0.0
    translation_x: float = 0.0
    translation_y: float = 0.0
    strength: float = 0.65
    prompt_weight: float = 1.0

    def __post_init__(self):
        """Validate keyframe parameters."""
        if self.frame < 0:
            raise ValueError(f"Frame must be non-negative, got {self.frame}")
        if self.time < 0:
            raise ValueError(f"Time must be non-negative, got {self.time}")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be 0-1, got {self.strength}")


@dataclass
class VideoResult:
    """
    Result from video generation.

    Attributes:
        video_path: Path to the generated video file
        frames_generated: Number of frames generated
        duration_seconds: Video duration in seconds
        fps: Frames per second
        style: Style preset used
    """
    video_path: str
    frames_generated: int
    duration_seconds: float
    fps: int
    style: str

    @property
    def file_size_mb(self) -> Optional[float]:
        """Get file size in megabytes, if available."""
        import os
        try:
            return os.path.getsize(self.video_path) / (1024 * 1024)
        except (OSError, IOError):
            return None


@dataclass
class StylePreset:
    """
    Visual style preset for video generation.

    Attributes:
        name: Human-readable name
        description: Description of the style
        prompt_base: Base prompt for Stable Diffusion
        negative_prompt: Negative prompt
        color_coherence: Color coherence mode ("LAB", "HSV", "None")
        motion_scale: Scale factor for motion effects
        strength_base: Base denoising strength
        guidance_scale: CFG scale for generation
    """
    name: str
    description: str
    prompt_base: str
    negative_prompt: str = "blurry, low quality, deformed"
    color_coherence: str = "LAB"
    motion_scale: float = 1.0
    strength_base: float = 0.65
    guidance_scale: float = 7.5


@dataclass
class GenerationConfig:
    """
    Configuration for video generation.

    Attributes:
        model_id: HuggingFace model ID
        width: Output video width
        height: Output video height
        fps: Frames per second
        max_frames: Maximum number of frames
        num_inference_steps: Diffusion steps per frame
        guidance_scale: CFG scale
        seed: Random seed (None for random)
    """
    model_id: str = "runwayml/stable-diffusion-v1-5"
    width: int = 512
    height: int = 512
    fps: int = 15
    max_frames: int = 120
    num_inference_steps: int = 25
    guidance_scale: float = 7.5
    seed: Optional[int] = None

    def __post_init__(self):
        """Validate generation config."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Dimensions must be positive: {self.width}x{self.height}")
        if self.fps <= 0:
            raise ValueError(f"FPS must be positive, got {self.fps}")
        if self.max_frames <= 0:
            raise ValueError(f"Max frames must be positive, got {self.max_frames}")


# Style motion parameters
@dataclass
class MotionParams:
    """
    Motion parameters for a style.

    Attributes:
        base_zoom: Base zoom level
        beat_zoom: Zoom change on beats
        rms_zoom: Zoom change based on RMS
        base_angle: Base rotation angle
        onset_angle: Rotation change on onsets
        base_trans_x: Base X translation
        spectral_trans_x: X translation based on spectral
        base_trans_y: Base Y translation
        rms_trans_y: Y translation based on RMS
        base_strength: Base denoising strength
    """
    base_zoom: float = 1.0
    beat_zoom: float = 0.05
    rms_zoom: float = 0.02
    base_angle: float = 0.0
    onset_angle: float = 2.0
    base_trans_x: float = 0.0
    spectral_trans_x: float = 5.0
    base_trans_y: float = 0.0
    rms_trans_y: float = 3.0
    base_strength: float = 0.65
