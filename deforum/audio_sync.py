"""
AudioSyncEngine - Extract audio features for Deforum animation
Syncs visual generation to beats, onsets, and note events
"""

import numpy as np
import librosa
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class AudioFeatures:
    """Extracted audio features for animation sync."""
    duration: float           # Total duration in seconds
    bpm: float                # Estimated BPM
    beat_times: np.ndarray    # Beat timestamps
    onset_times: np.ndarray   # Note onset timestamps
    onset_strengths: np.ndarray  # Onset strength values
    rms_curve: np.ndarray     # RMS energy curve
    spectral_curve: np.ndarray  # Spectral centroid curve
    sample_rate: int          # Sample rate used


@dataclass
class AnimationKeyframe:
    """A keyframe for Deforum animation."""
    frame: int
    time: float
    zoom: float
    angle: float
    translation_x: float
    translation_y: float
    strength: float  # Denoising strength
    prompt_weight: float


class AudioSyncEngine:
    """
    Extract audio features and generate Deforum animation parameters.
    
    Maps audio events to visual motion:
    - Beats → camera zoom pulses
    - Onsets → rotation/translation
    - RMS → motion intensity
    - Spectral centroid → color/style shifts
    """
    
    def __init__(
        self,
        fps: int = 15,
        onset_sensitivity: float = 0.5,
        beat_strength_scale: float = 2.0
    ):
        """
        Initialize AudioSyncEngine.
        
        Args:
            fps: Frames per second for animation
            onset_sensitivity: Sensitivity for onset detection (0-1)
            beat_strength_scale: Multiplier for beat-triggered motion
        """
        self.fps = fps
        self.onset_sensitivity = onset_sensitivity
        self.beat_strength_scale = beat_strength_scale
    
    def analyze_audio(self, audio_path: str) -> AudioFeatures:
        """
        Extract audio features for animation sync.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioFeatures with timing and energy data
        """
        print(f"🎵 Analyzing audio for sync: {Path(audio_path).name}")
        
        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=22050, mono=True)
        duration = len(audio) / sr
        
        # Beat tracking
        tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Onset detection
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            backtrack=True,
            delta=self.onset_sensitivity
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        onset_strengths = onset_env[onset_frames] if len(onset_frames) > 0 else np.array([])
        
        # Normalize onset strengths
        if len(onset_strengths) > 0:
            onset_strengths = onset_strengths / np.max(onset_strengths)
        
        # RMS energy
        rms = librosa.feature.rms(y=audio)[0]
        rms = rms / (np.max(rms) + 1e-8)  # Normalize
        
        # Spectral centroid
        spectral = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        spectral = (spectral - np.min(spectral)) / (np.max(spectral) - np.min(spectral) + 1e-8)
        
        print(f"   ✅ BPM: {tempo:.1f}, Beats: {len(beat_times)}, Onsets: {len(onset_times)}")
        
        return AudioFeatures(
            duration=duration,
            bpm=float(tempo),
            beat_times=beat_times,
            onset_times=onset_times,
            onset_strengths=onset_strengths,
            rms_curve=rms,
            spectral_curve=spectral,
            sample_rate=sr
        )
    
    def generate_keyframes(
        self,
        features: AudioFeatures,
        max_frames: int = 120,
        style: str = "guitar_hero"
    ) -> List[AnimationKeyframe]:
        """
        Generate Deforum animation keyframes from audio features.
        
        Args:
            features: AudioFeatures from analyze_audio()
            max_frames: Maximum number of frames
            style: Animation style preset
            
        Returns:
            List of AnimationKeyframe objects
        """
        num_frames = min(max_frames, int(features.duration * self.fps))
        keyframes = []
        
        print(f"🎬 Generating {num_frames} animation keyframes ({style} style)")
        
        # Style-specific base parameters
        style_params = self._get_style_params(style)
        
        for frame in range(num_frames):
            time = frame / self.fps
            
            # Get interpolated audio values at this time
            rms_val = self._interpolate_at_time(features.rms_curve, time, features.duration)
            spectral_val = self._interpolate_at_time(features.spectral_curve, time, features.duration)
            
            # Check for nearby beats
            beat_intensity = self._beat_intensity(time, features.beat_times)
            
            # Check for nearby onsets
            onset_intensity, onset_strength = self._onset_intensity(
                time, features.onset_times, features.onset_strengths
            )
            
            # Calculate animation parameters
            zoom = style_params['base_zoom']
            zoom += beat_intensity * style_params['beat_zoom'] * self.beat_strength_scale
            zoom += rms_val * style_params['rms_zoom']
            
            angle = style_params['base_angle']
            angle += onset_intensity * onset_strength * style_params['onset_angle']
            
            trans_x = style_params['base_trans_x']
            trans_x += spectral_val * style_params['spectral_trans_x']
            
            trans_y = style_params['base_trans_y']
            trans_y += rms_val * style_params['rms_trans_y']
            
            # Denoising strength (lower = more coherent)
            strength = style_params['base_strength']
            strength -= beat_intensity * 0.1  # More creative on beats
            strength = max(0.3, min(0.9, strength))
            
            keyframes.append(AnimationKeyframe(
                frame=frame,
                time=time,
                zoom=zoom,
                angle=angle,
                translation_x=trans_x,
                translation_y=trans_y,
                strength=strength,
                prompt_weight=1.0
            ))
        
        return keyframes
    
    def _get_style_params(self, style: str) -> Dict:
        """Get animation parameters for a style."""
        styles = {
            'guitar_hero': {
                'base_zoom': 1.0,
                'beat_zoom': 0.05,
                'rms_zoom': 0.02,
                'base_angle': 0.0,
                'onset_angle': 2.0,
                'base_trans_x': 0.0,
                'spectral_trans_x': 5.0,
                'base_trans_y': 0.0,
                'rms_trans_y': 3.0,
                'base_strength': 0.65
            },
            'concert': {
                'base_zoom': 1.0,
                'beat_zoom': 0.03,
                'rms_zoom': 0.01,
                'base_angle': 0.0,
                'onset_angle': 1.0,
                'base_trans_x': 0.0,
                'spectral_trans_x': 2.0,
                'base_trans_y': 0.0,
                'rms_trans_y': 1.0,
                'base_strength': 0.55
            },
            'abstract': {
                'base_zoom': 1.02,
                'beat_zoom': 0.08,
                'rms_zoom': 0.04,
                'base_angle': 0.5,
                'onset_angle': 5.0,
                'base_trans_x': 0.0,
                'spectral_trans_x': 10.0,
                'base_trans_y': 0.0,
                'rms_trans_y': 8.0,
                'base_strength': 0.7
            },
            'acoustic': {
                'base_zoom': 1.0,
                'beat_zoom': 0.02,
                'rms_zoom': 0.01,
                'base_angle': 0.0,
                'onset_angle': 0.5,
                'base_trans_x': 0.0,
                'spectral_trans_x': 1.0,
                'base_trans_y': 0.0,
                'rms_trans_y': 0.5,
                'base_strength': 0.5
            }
        }
        return styles.get(style, styles['guitar_hero'])
    
    def _interpolate_at_time(
        self,
        curve: np.ndarray,
        time: float,
        duration: float
    ) -> float:
        """Interpolate curve value at a specific time."""
        if len(curve) == 0:
            return 0.0
        
        idx = int((time / duration) * len(curve))
        idx = max(0, min(idx, len(curve) - 1))
        return float(curve[idx])
    
    def _beat_intensity(self, time: float, beat_times: np.ndarray) -> float:
        """Calculate beat intensity at a time (1.0 near beat, 0.0 away)."""
        if len(beat_times) == 0:
            return 0.0
        
        # Find distance to nearest beat
        distances = np.abs(beat_times - time)
        min_dist = np.min(distances)
        
        # Decay function (1.0 at beat, 0.0 at 0.1s away)
        decay_time = 0.1
        intensity = max(0.0, 1.0 - min_dist / decay_time)
        
        return intensity
    
    def _onset_intensity(
        self,
        time: float,
        onset_times: np.ndarray,
        onset_strengths: np.ndarray
    ) -> Tuple[float, float]:
        """Calculate onset intensity and strength at a time."""
        if len(onset_times) == 0:
            return 0.0, 0.0
        
        distances = np.abs(onset_times - time)
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]
        
        decay_time = 0.05
        intensity = max(0.0, 1.0 - min_dist / decay_time)
        
        strength = onset_strengths[min_idx] if min_idx < len(onset_strengths) else 0.5
        
        return intensity, strength
    
    def export_deforum_schedule(
        self,
        keyframes: List[AnimationKeyframe]
    ) -> Dict[str, str]:
        """
        Export keyframes as Deforum animation schedule strings.
        
        Returns:
            Dictionary with schedule strings for each parameter
        """
        zoom_schedule = []
        angle_schedule = []
        trans_x_schedule = []
        trans_y_schedule = []
        strength_schedule = []
        
        for kf in keyframes:
            zoom_schedule.append(f"{kf.frame}:({kf.zoom:.3f})")
            angle_schedule.append(f"{kf.frame}:({kf.angle:.2f})")
            trans_x_schedule.append(f"{kf.frame}:({kf.translation_x:.2f})")
            trans_y_schedule.append(f"{kf.frame}:({kf.translation_y:.2f})")
            strength_schedule.append(f"{kf.frame}:({kf.strength:.3f})")
        
        return {
            "zoom": ", ".join(zoom_schedule),
            "angle": ", ".join(angle_schedule),
            "translation_x": ", ".join(trans_x_schedule),
            "translation_y": ", ".join(trans_y_schedule),
            "strength_schedule": ", ".join(strength_schedule)
        }
